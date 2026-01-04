from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Note

class NotesService:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def create_note(self, content: str) -> Note:
        print(f"[NotesService] Creating note for owner_id='{self.user_id}' with content: '{content[:20]}...'")
        note = Note(owner_id=self.user_id, content=content)
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def get_my_notes(self) -> list[Note]:
        print(f"[NotesService] Fetching notes for owner_id='{self.user_id}'")
        # RBAC: Only fetch notes where owner_id matches the current user
        result = await self.db.execute(select(Note).where(Note.owner_id == self.user_id))
        print(f"[NotesService] Found {len(result.scalars().all())} notes for owner_id='{self.user_id}'")
        return result.scalars().all()
