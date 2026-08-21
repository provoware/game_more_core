import tempfile
import unittest

from bunkerfrequenz.application.presentation_events import get_confirmed_events
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


ALLOWED = {"character.profile_updated"}
CTX = JournalContext(
    "2026-08-21T19:50:00+02:00",
    "session-events",
    "player-events",
    "character",
    "char.pppoppi",
    "command-events",
    "presentation",
    "0.5.2-alpha.1",
    "char.pppoppi",
)


class PresentationEventsTest(unittest.TestCase):
    def test_returns_exact_confirmed_records_in_requested_order_and_detached(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = CharacterProfileService(kernel)
            character = CharacterState("char.pppoppi", "PPPOPPI")
            first = service.update(
                character,
                {"alias": "A"},
                event_id="evt-a",
                transaction_id="tx-a",
                context=CTX,
            )
            service.update(
                first,
                {"motto": "B"},
                event_id="evt-b",
                transaction_id="tx-b",
                context=CTX,
            )

            records = get_confirmed_events(("evt-b", "evt-a"), kernel)
            self.assertEqual([record["event_id"] for record in records], ["evt-b", "evt-a"])
            records[0]["payload"]["new"]["motto"] = "changed"
            persisted = {record["event_id"]: record for record in kernel.read_records()}
            self.assertEqual(persisted["evt-b"]["payload"]["new"]["motto"], "B")

    def test_missing_or_duplicate_requested_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            with self.assertRaises(PersistenceError):
                get_confirmed_events(("missing",), kernel)
            with self.assertRaises(ValueError):
                get_confirmed_events(("same", "same"), kernel)
            with self.assertRaises(ValueError):
                get_confirmed_events(("",), kernel)

    def test_empty_confirmation_is_empty_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            self.assertEqual(get_confirmed_events((), kernel), ())
            self.assertEqual(kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
