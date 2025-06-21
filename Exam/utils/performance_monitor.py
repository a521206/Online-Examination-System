"""
Performance monitoring utility for Django views and scripts.

Usage:
- Use @monitor_performance("function_name") as a decorator on any view or function to log execution time and query count.
- Call log_query_performance() after a request to print a summary of all queries and their times.
- Use get_slow_queries(threshold) to get a list of slow queries.
- Use print_last_queries(n) to print the last n queries and their times for debugging.
"""
import time
import functools
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def monitor_performance(func_name=None):
    """
    Decorator to monitor function performance and database queries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            initial_queries = len(connection.queries)
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                total_queries = len(connection.queries) - initial_queries
                execution_time = end_time - start_time
                
                # Log performance metrics
                logger.info(
                    f"Performance: {func_name or func.__name__} - "
                    f"Time: {execution_time:.3f}s, "
                    f"Queries: {total_queries}"
                )
                
                # Log slow queries if DEBUG is enabled
                if settings.DEBUG and execution_time > 0.5:
                    logger.warning(
                        f"Slow function detected: {func_name or func.__name__} "
                        f"took {execution_time:.3f}s with {total_queries} queries"
                    )
                
                return result
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.error(
                    f"Error in {func_name or func.__name__}: {str(e)} "
                    f"(Time: {execution_time:.3f}s)"
                )
                raise
        
        return wrapper
    return decorator

def get_query_count():
    """Get the current number of database queries"""
    return len(connection.queries)

def get_slow_queries(threshold=0.1):
    """Get queries that took longer than the threshold (in seconds)"""
    slow_queries = []
    for query in connection.queries:
        try:
            if float(query.get('time', 0)) > threshold:
                slow_queries.append(query)
        except Exception:
            continue
    return slow_queries

def log_query_performance():
    """Log all queries and their performance"""
    if not settings.DEBUG:
        return
    
    total_time = sum(float(q.get('time', 0)) for q in connection.queries if 'time' in q)
    total_queries = len(connection.queries)
    
    logger.info(f"Total queries: {total_queries}, Total time: {total_time:.3f}s")
    
    # Log slow queries
    slow_queries = get_slow_queries(0.1)
    if slow_queries:
        logger.warning(f"Found {len(slow_queries)} slow queries (>0.1s)")
        for i, query in enumerate(slow_queries[:5]):  # Log first 5 slow queries
            logger.warning(f"Slow query {i+1}: {query.get('sql', '')[:100]}... "
                          f"(Time: {query.get('time', 0)}s)")

def print_last_queries(n=10):
    """Print the last n queries and their times for debugging slow pages."""
    queries = connection.queries[-n:]
    print(f"\nLast {len(queries)} queries:")
    for i, q in enumerate(queries, 1):
        sql = q.get('sql', '').replace('\n', ' ')
        t = q.get('time', '?')
        print(f"{i}. {sql[:120]}... (Time: {t}s)") 