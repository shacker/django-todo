import django.dispatch
from django.dispatch import receiver

from todo.utils import toggle_task_completed

# ### REGISTER SIGNALS ###

# Demonstrates registering a custom signal
pizza_done = django.dispatch.Signal(providing_args=["toppings", "size", "task_id"])


# ### HANDLE SIGNALS ###

# Demonstrates receiving a custom signal
# (which in turn calls an existing todo function, but could do anything)
@receiver(pizza_done)
def toggle_task_handler(sender, **kwargs):
    print(sender)
    print(kwargs)
    task_id = kwargs.get("task_id")
    results = toggle_task_completed(task_id)
    print(results)

    print("Request finished!")
