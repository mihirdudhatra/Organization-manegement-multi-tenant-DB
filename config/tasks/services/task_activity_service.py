from tasks.models import TaskActivity, Task
from system.models import User
from typing import Optional


class TaskActivityService:
    """
    Handles all audit logging.
    """

    @staticmethod
    def log(
        *,
        db,
        task: Task,
        action: str,
        user_id: Optional[User.id],
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        comment: str = "",
    ) -> None:
        """
        Time: O(1)
        Space: O(1)
        """
        TaskActivity.objects.using(db).create(
            task=task,
            action=action,
            old_value=old_value,
            new_value=new_value,
            comment=comment,
            performed_by=user_id,
        )
