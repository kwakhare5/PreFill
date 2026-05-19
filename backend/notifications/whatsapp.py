"""
WhatsApp Notification Gateway — Task 3.2
STATUS: NOT YET IMPLEMENTED — placeholder file.

Planned implementation (Task 3.2):
  - POST /api/webhook/whatsapp  — Twilio webhook receiver
    Parses incoming WhatsApp messages (YES / NO / STOP) from users.
    Looks up the latest pending RestockAlert for this phone number.
    Routes to the LangGraph restock_agent for stateful conversation handling.

  - send_whatsapp_message(to: str, body: str) → None
    Wrapper around Twilio Client to send outbound WhatsApp messages.
    Used by the scheduler and check-now endpoint to deliver alerts.

Dependencies:
  - twilio (installed in requirements.txt)
  - settings.TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM
  - backend.agents.restock_agent.RestockAgent

See IMPLEMENTATION_PLAN.md Task 3.2 for the complete code spec.
"""

# Implementation starts in Task 3.2 — do not add code here yet.
