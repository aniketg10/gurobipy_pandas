"""
Top-level API functions
"""

from typing import overload, Union, Optional

import gurobipy as gp
from gurobipy import GRB
import pandas as pd

from gurobipy_pandas.variables import (
    add_vars_from_index,
    add_vars_from_dataframe,
)
from gurobipy_pandas.constraints import add_constrs_from_series


# Index/Series variant (attribute arguments must be values or series)
@overload
def add_vars(
    model: gp.Model,
    pandas_obj: Union[pd.Index, pd.Series],
    *,
    name: Optional[Union[str, pd.Series]] = None,
    lb: Union[float, pd.Series] = 0.0,
    ub: Union[float, pd.Series] = GRB.INFINITY,
    obj: Union[float, pd.Series] = 0.0,
    vtype: Union[str, pd.Series] = GRB.CONTINUOUS,
) -> pd.Series:
    ...  # pragma: no cover


# DataFrame variant (attribute arguments must be values or column names)
@overload
def add_vars(
    model: gp.Model,
    pandas_obj: pd.DataFrame,
    *,
    name: Optional[str] = None,
    lb: Union[float, str] = 0.0,
    ub: Union[float, str] = GRB.INFINITY,
    obj: Union[float, str] = 0.0,
    vtype: str = GRB.CONTINUOUS,
) -> pd.Series:
    ...  # pragma: no cover


def add_vars(
    model,
    pandas_obj,
    *,
    name=None,
    lb=0.0,
    ub=GRB.INFINITY,
    obj=0.0,
    vtype=GRB.CONTINUOUS,
):
    """Add a variable to the given model for each entry in the given pandas
    Index, Series, or DataFrame.

    :param model: A Gurobi model to which new variables will be added
    :type model: :class:`gurobipy.Model`
    :param pandas_obj: A pandas Index, Series, or DataFrame
    :param name: If provided, used as base name for new Gurobi variables
        and the name of the returned series
    :type name: str, optional
    :param lb: Lower bound for created variables. Can be a single numeric
        value. If :pandas_obj is an Index or Series, can be a Series aligned
        with :pandas_obj. If :pandas_obj is a dataframe, can be a string
        referring to a column of :pandas_obj. Defaults to 0.0
    :type lb: float, str, or pd.Series, optional
    :return: A Series of vars with the the index of :pandas_obj
    :rtype: :class:`pd.Series`
    """
    if isinstance(pandas_obj, pd.Index):
        # Use the given index as the base object. All attribute arguments must
        # be single values, or series aligned with the index.
        return add_vars_from_index(
            model, pandas_obj, name=name, lb=lb, ub=ub, obj=obj, vtype=vtype
        )
    elif isinstance(pandas_obj, pd.Series):
        # Use the index of the given series as the base object. All attribute
        # arguments must be single values, or series on the same index as the
        # given series.
        return add_vars_from_index(
            model, pandas_obj.index, name=name, lb=lb, ub=ub, obj=obj, vtype=vtype
        )
    elif isinstance(pandas_obj, pd.DataFrame):
        # Use the given dataframe as the base object. All attribute arguments
        # must be single values, or names of columns in the given dataframe.
        return add_vars_from_dataframe(
            model, pandas_obj, name=name, lb=lb, ub=ub, obj=obj, vtype=vtype
        )
    else:
        raise ValueError("`pandas_obj` must be an index, series, or dataframe")


def add_constrs(
    model: gp.Model,
    lhs: Union[pd.Series, float],
    sense: str,
    rhs: Union[pd.Series, float],
    *,
    name: Optional[str] = None,
) -> pd.Series:
    """Add a constraint to the model for each row in lhs & rhs.

    :param model: A Gurobi model to which new constraints will be added
    :type model: :class:`gurobipy.Model`
    :param lhs: A series or numeric value
    :type lhs: pd.Series
    :param sense: Constraint sense
    :type sense: str
    :param rhs: A series or numeric value
    :type rhs: pd.Series
    :param name: Used as the returned series name, as well as the base
        name for added Gurobi constraints. Constraint name suffixes
        come from the lhs/rhs index.
    :type name: str
    :return: A Series of Constr objects
    :rtype: :class:`pd.Series`
    """
    return add_constrs_from_series(model, lhs, sense, rhs, name=name)