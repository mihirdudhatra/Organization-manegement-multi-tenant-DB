from celery import shared_task
from django.core.mail import send_mail
from system.models import User
from tasks.models import Task


@shared_task(bind=True, max_retries=3)
def notify_assignment(self, user_id: int, task_id: int):
    """Mock sending assignment notification to a user."""
    try:
        user = User.objects.get(id=user_id)
        task = Task.objects.get(id=task_id)
    except (User.DoesNotExist, Task.DoesNotExist):
        return

    subject = f"You've been assigned to task: {task.title}"
    message = f"Hi {user.username},\n\nYou have been assigned to task '{task.title}' in project {task.project}."

    # In prod this would send real emails; here we attempt and ignore failures
    try:
        send_mail(subject, message, 'no-reply@example.com', [user.email])
    except Exception:
        # For development, just log to stdout (Celery worker logs)
        print(f"Notification (assignment) for user={user.username}, task={task.id}")


@shared_task(bind=True, max_retries=3)
def notify_status_change(self, task_id: int, old_status: str, new_status: str):
    """Notify watchers about status changes (mock)."""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return

    subject = f"Task status changed: {task.title}"
    message = f"Task '{task.title}' changed from {old_status} to {new_status}."

    # Send to the assigned user if present
    if task.assigned_to and task.assigned_to.email:
        try:
            send_mail(subject, message, 'no-reply@example.com', [task.assigned_to.email])
        except Exception:
            print(f"Notification (status) for task={task.id} to {task.assigned_to.username}")
