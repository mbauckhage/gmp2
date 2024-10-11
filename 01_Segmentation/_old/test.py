import time
import sys

def timer_decorator(func):
    """
    Decorator to measure the elapsed time of a function.
    
    Parameters:
    func (callable): The function to be decorated.
    
    Returns:
    callable: The wrapped function that measures execution time.
    """
    def wrapper(*args, **kwargs):
        # Start the timer
        start_time = time.time()  
        print(f"Starting '{func.__name__}'...")

        # Start a loop to display the running clock
        try:
            while True:
                elapsed_time = time.time() - start_time
                # Clear the line and print the elapsed time
                sys.stdout.write(f'\rElapsed time: {elapsed_time:.2f} seconds')
                sys.stdout.flush()  # Ensure the output is displayed immediately
                
                # Call the original function and check if it returns
                result = func(*args, **kwargs)
                
                # Break the loop after the function call completes
                break
        finally:
            # Print the final elapsed time
            end_time = time.time()  
            total_elapsed_time = end_time - start_time
            print(f'\rElapsed time for {func.__name__}: {total_elapsed_time:.2f} seconds\n')

        return result  # Return the result of the original function

    return wrapper

# Example of using the timer decorator
@timer_decorator
def example_function(duration):
    """
    Example function that simulates work by sleeping for a given duration.
    
    Parameters:
    duration (int): Duration to sleep in seconds.
    """
    time.sleep(duration)  # Simulate a task by sleeping

# Call the example function
example_function(3)  # This will take about 3 seconds
