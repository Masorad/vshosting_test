import inspect
from contextlib import contextmanager
from functools import wraps
import os

try:
    maketrans = ''.maketrans
except AttributeError:
    # fallback for Python 2
    from string import maketrans


class CartesianProduct(object):
    """
    Strategy to use in @with_parameters decorator.
    It would allow all possible combinations of input parameters.
    """

    def combine(self, args, kwargs, **flags):
        return generate_combinations(kwargs)


def enable_parametrized_tests(run_tests_with_default_values=(os.getenv('RUN_TESTS_WITH_DEFAULT_VALUES',
                                                                       'False').lower() == 'true'),
                              run_tests_with_default_values_only=(os.getenv('RUN_TESTS_WITH_DEFAULT_VALUES_ONLY',
                                                                            'False').lower() == 'true')):
    """
    Class decorator to use in conjunction with @with_parameters method decorator.
    Use run_tests_with_default_values=True parameter when running single test from your IDE (e.g. Eclipse or IntelliJ)
    :param run_tests_with_default_values: whether to keep existing test method relying on its default values instead of
    having just the synthetic test methods with substituted parameter value combinations.
    :return: modified class object
    """

    def test_parametrizer(cls):
        # find all parameterized methods inside the test case class
        tests_with_parametrization = [
            f for f in (getattr(cls, name) for name in dir(cls)) if callable(f) and hasattr(f, 'parametrized_tests')
        ]
        for test_with_parametrization in tests_with_parametrization:
            for parametrized_test in test_with_parametrization.parametrized_tests:
                # register all synthetic test methods into the class (unless run_tests_with_default_values_only==True)
                if not run_tests_with_default_values_only:
                    setattr(cls, parametrized_test.__name__, parametrized_test)
            if not (run_tests_with_default_values or run_tests_with_default_values_only):
                # remove the original parameterized method so it does not interfere with coverage
                delattr(cls, test_with_parametrization.__name__)
        return cls

    return test_parametrizer


def generate_test(test, parameters):
    @wraps(test)
    def synthetic_test_method(self, **kwargs):
        kwargs.update(**parameters)
        test(self, **kwargs)

    synthetic_test_method.__name__ += name_suffix(parameters)
    return synthetic_test_method


def name_suffix(parameters):
    return '.' + ' '.join((str(value) for value in parameters.values())).translate(maketrans('.,', '_ '))


def generate_combinations(dict_of_lists, **flags):
    if not dict_of_lists:
        yield dict()
    else:
        key, values = dict_of_lists.popitem()
        for combination in generate_combinations(dict_of_lists, **flags):
            for value in values:
                combination[key] = value
                yield combination.copy()


def with_parameters(*args, **kwargs):
    """
    Test method decorator to allow parametrized tests.
    A special strategy key allows to choose among CartesianProduct and Pairwise way of combining input parameter values.


    @with_parameters(
        strategy=Pairwise,
        currency=['EUR', 'USD', 'GBP', 'CHF'],
        amount=['10.01', '50033', '50033.27', '123.45'])
    :param args: list of dictionaries to use with Sequential strategy
    :param kwargs: dictionary of named lists - see the example above
    :return: decorated test method

    """

    def wrap(test):
        strategy = kwargs.pop('strategy', CartesianProduct)()

        test.parametrized_tests = sorted([generate_test(test, parameters)
                                          for parameters in strategy.combine(args, kwargs)], key=lambda x: x.__name__)

        return test

    return wrap


@contextmanager
def fixed_kwargs(function, **kwargs):
    parameters = inspect.getfullargspec(function)
    if not parameters[2]:
        correct_kwargs = {key: value for key, value in kwargs.items() if key in parameters[0]}
        yield correct_kwargs
    else:
        yield kwargs
