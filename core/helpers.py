from functools import wraps
from flask import flash, redirect, url_for

def handle_error(func):
    """
    Decorator that wraps a function with error handling for ValueError exceptions.
    
    When the decorated function raises a ValueError, the error message is flashed
    to the user and the user is redirected to the index page.
    
    Args:
        func: The function to be decorated.
    
    Returns:
        wrapper: The decorated function that includes error handling.
    
    Raises:
        ValueError: Caught and handled by displaying a flash message and redirecting to index.
    
    Example:
        @handle_error
        def my_function():
            raise ValueError("Something went wrong")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for("index"))
    return wrapper