import datetime
import decimal
from typing import List, Any, Optional
from sqlalchemy import or_, and_, desc, select
from sqlalchemy.orm import selectinload
from models import get_session, run_in_thread


def get_columns_name(model: object):
    from models.company_owner import Company
    from models.employee import Employee
    from models.freelancer import FreeLancer
    from models.company_owner import CompanyOwner

    if isinstance(model, Employee):
        return [
            "id",
            "name",
            "salary",
            "payment_status",
            "loan_from_salary",
            "rem_from_salary",
            "amount_paid",
            "amount_settled",
            "loan_date",
            "payment_date",
        ]
    elif isinstance(model, Company):
        return [
            "id",
            "shipping_id",
            "loan_amount",
            "date_of_debt",
            "paid_amounts",
            "rem_amounts",
            "note",
            "monthly_payment_due_date",
        ]
    elif isinstance(model, FreeLancer):
        return ["id", "other_costs", "amount", "note", "date"]
    elif isinstance(model, CompanyOwner):
        return [
            "id",
            "payment_date",
            "order_date",
            "payment_status",
            "total_profit_from_order",
            "total_discount",
            "retrieved_order",
            "coupon_code",
            "payment_method",
            "total_demand",
            "shipping_company",
            "salla_total",
            "cost",
            "order_status",
            "order_number",
            "store_name",
        ]
    else:
        raise Exception(f"There's name class named {model}")


def sqlalchemy_to_python_type(obj):
    from models.constant import OrderStatus
    from models.employee import PaymentStatus

    default_values = {}
    excluded_columns = ["updated_at", "created_at", "updated_at"]
    for column in obj.__table__.columns:
        if column.name in excluded_columns:
            continue
        name = column.name
        default_value = column.default.arg if column.default else None
        py_type = column.type.python_type
        if py_type == int:
            default_values[name] = decimal.Decimal(0)
        elif py_type == str:
            default_values[name] = str("")
        elif py_type == decimal.Decimal:
            default_values[name] = decimal.Decimal(0)
        elif py_type == datetime.datetime:
            default_values[name] = datetime.datetime.now().strftime("YYYY-MM-DD")
        elif py_type == datetime.date:
            default_values[name] = datetime.date.today()
        elif py_type == PaymentStatus:
            default_values[name] = PaymentStatus.get_str(PaymentStatus.PENDING)
        elif py_type == OrderStatus:
            default_values[name] = OrderStatus.get_str(OrderStatus.PENDING)
        else:
            raise Exception(f"Type not found for column {column.name} {py_type}")
    default_values["id"] = int(-1)
    return default_values


class DynamicSearch:

    @classmethod
    def where(
        cls,
        column: str,
        value: Any,
        session,
        operator: str = "eq",
        order_by: str = "created_at",
        order_direction: str = "desc",
        limit: Optional[int] = None,
        **kwargs,
    ) -> List[Any]:
        """
        Enhanced search method with support for different operators and ordering.

        Args:
            column: The column name to search in
            value: The value to search for
            session: SQLAlchemy session
            operator: Comparison operator ('eq', 'like', 'in', 'gt', 'lt', 'between', etc.)
            order_by: Column to order results by
            order_direction: Sort direction ('asc' or 'desc')
            limit: Optional limit for number of results
            **kwargs: Additional arguments for specific operators

        Returns:
            List of matching records
        """

        print("xxxx=>", kwargs)

        try:
            # Get column attribute safely
            column_attr = getattr(cls, column, None)
            if column_attr is None:
                raise ValueError(f"Column {column} not found in {cls.__name__}")

            # Get ordering column
            order_column = getattr(cls, order_by, None)
            if order_column is None:
                raise ValueError(f"Order column {order_by} not found in {cls.__name__}")

            # Build query
            query = session.query(cls)

            # Apply filter based on operator
            filter_expr = cls._build_filter(column_attr, value, operator, **kwargs)
            query = query.filter(filter_expr)

            # Apply ordering
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)

            # Apply limit if specified
            if limit is not None:
                query = query.limit(limit)

            # Eager load relationships
            for relationship_name in cls.__mapper__.relationships.keys():
                query = query.options(selectinload(getattr(cls, relationship_name)))

            return query.all()

        except Exception as e:
            raise Exception(f"Search error in {cls.__name__}: {str(e)}")

    @staticmethod
    def _build_filter(column_attr, value: Any, operator: str, **kwargs):
        """
        Build filter expression based on operator

        Args:
            column_attr: SQLAlchemy column attribute
            value: Value to filter on
            operator: Comparison operator
            **kwargs: Additional arguments for specific operators

        Returns:
            SQLAlchemy filter expression
        """
        operator = operator.lower()

        # Standard comparison operators
        if operator == "eq":
            return column_attr == value
        elif operator == "neq":
            return column_attr != value
        elif operator == "like":
            return column_attr.like(f"%{value}%")
        elif operator == "ilike":
            return column_attr.ilike(f"%{value}%")
        elif operator == "in":
            return column_attr.in_(
                value if isinstance(value, (list, tuple)) else [value]
            )
        elif operator == "gt":
            return column_attr > value
        elif operator == "gte":
            return column_attr >= value
        elif operator == "lt":
            return column_attr < value
        elif operator == "lte":
            return column_attr <= value

        # Between operator with enhanced date range support
        elif operator == "between":
            # Validate between requires start and end values
            if "start" not in kwargs or "end" not in kwargs:
                raise ValueError(
                    "'between' operator requires 'start' and 'end' arguments"
                )

            start = kwargs.get("start")
            end = kwargs.get("end")

            # Handle different input types
            if isinstance(start, (datetime.date, datetime.datetime)) and isinstance(
                end, (datetime.date, datetime.datetime)
            ):
                # Date/datetime range
                return column_attr.between(start, end)
            elif isinstance(start, (int, float)) and isinstance(end, (int, float)):
                # Numeric range
                return column_attr.between(start, end)
            else:
                raise ValueError(
                    "Invalid types for 'between' operator. Must be date, datetime, int, or float."
                )

        # Complex search with multiple conditions
        elif operator == "or":
            if not isinstance(value, list):
                raise ValueError("'or' operator requires a list of values")

            # Create OR conditions
            or_conditions = [column_attr == val for val in value]
            return or_(*or_conditions)

        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def search_with_relations(self, filters):
        """
        Search across related tables with multiple filters

        Args:
            filters: Dict of {model_name.column_name: value} pairs

        Returns:
            List of matching objects with a session that must be closed
        """
        # Create a new session that will stay open
        with get_session() as session:
            try:
                # Start with the base query
                query = select(self.__class__)

                # Process filters and add joins as needed
                for filter_key, value in filters.items():
                    if "." in filter_key:
                        # This is a related model filter
                        relation_name, column_name = filter_key.split(".")

                        # Add the join if it's a relationship
                        if hasattr(self.__class__, relation_name):
                            relation = getattr(self.__class__, relation_name)
                            related_model = relation.property.mapper.class_
                            query = query.join(relation)

                            # Add the filter on the related model
                            if hasattr(related_model, column_name):
                                related_column = getattr(related_model, column_name)
                                query = query.filter(related_column == value)
                    else:
                        # This is a direct column filter
                        if hasattr(self.__class__, filter_key):
                            column = getattr(self.__class__, filter_key)
                            query = query.filter(column == value)

                # Get all relationship attributes for this class
                mapper = self.__class__.__mapper__
                relationship_properties = [
                    p.key for p in mapper.iterate_properties if hasattr(p, "direction")
                ]

                # Add eager loading options for ALL relationships
                for rel_name in relationship_properties:
                    relation = getattr(self.__class__, rel_name)
                    query = query.options(selectinload(relation))

                # Execute the query
                result = session.execute(query)
                items = result.scalars().all()

                # Keep the session open and return a wrapper that will close it when done
                return items
            except Exception as e:
                session.close()
                print(f"Error in search_with_relations: {e}")
                return []

    @classmethod
    def search(
        cls,
        session,
        filters: List[dict],
        combine_with: str = "and",
        order_by: str = "created_at",
        order_direction: str = "desc",
        limit: Optional[int] = None,
    ) -> List[Any]:
        """
        Advanced search with multiple filters.

        Args:
            session: SQLAlchemy session
            filters: List of filter dictionaries with keys 'column', 'value', and 'operator'
            combine_with: How to combine multiple filters ('and' or 'or')
            order_by: Column to order results by
            order_direction: Sort direction ('asc' or 'desc')
            limit: Optional limit for number of results

        Returns:
            List of matching records
        """
        try:
            # Build filter expressions
            filter_expressions = []
            for filter_dict in filters:
                column = getattr(cls, filter_dict["column"])
                filter_expr = cls._build_filter(
                    column, filter_dict["value"], filter_dict.get("operator", "eq")
                )
                filter_expressions.append(filter_expr)

            # Combine filters
            if combine_with.lower() == "or":
                combined_filter = or_(*filter_expressions)
            else:
                combined_filter = and_(*filter_expressions)

            # Build query
            query = session.query(cls)
            query = query.filter(combined_filter)

            # Apply ordering
            order_column = getattr(cls, order_by)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)

            # Apply limit
            if limit is not None:
                query = query.limit(limit)

            return query.all()

        except Exception as e:
            raise Exception(f"Advanced search error in {cls.__name__}: {str(e)}")
