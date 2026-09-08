"""
STEP 3 — Minimal real Rime voice path.

Purpose: prove that real audio comes out of Rime through a live LiveKit room,
with zero other moving parts (no STT, no LLM, no interruption logic).

This is deliberately throwaway scaffolding — it will be replaced by
agent.py once the full pipeline (Step 4+) is in place. Keep it around
as a fast sanity check: if Rime ever "goes silent" later, run this
file first to isolate whether the problem is Rime or your pipeline.

Run:
    python backend/agent_step3_rime_only.py dev

Expected behavior:
    - Agent joins the LiveKit room specified by LIVEKIT_URL.
    - The moment a participant (you, via the LiveKit Agents Playground
      or your frontend) joins, you should hear a real Rime voice say
      the hardcoded line below.
    - No mic input is processed at this stage — this only proves the
      OUTPUT half of the pipeline.

Known version sensitivity:
    This uses the WorkerOptions/cli.run_app entrypoint pattern, which
    is the long-standing, widely-documented way to run a LiveKit agent
    job. Some very recent LiveKit docs show a newer AgentServer /
    @server.rtc_session decorator pattern instead. Run
    `pip show livekit-agents` after install and tell me the version —
    if it's a recent 1.x release using the new pattern, this file's
    entrypoint wiring (marked below) is the only part that needs to
    change; everything else stays the same.
"""

import logging

from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import rime

load_dotenv()

logger = logging.getLogger("dhwani.step3")
logging.basicConfig(level=logging.INFO)

RIME_MODEL = "mist"  # explicit on purpose — never rely on the plugin default
RIME_SPEAKER = "rainforest"  # placeholder; swap for whichever speaker Person 3 wants on the demo dashboard


class GreeterOnly(Agent):
    """An Agent with no LLM/STT wired up. Exists only to satisfy AgentSession's
    interface for this throwaway test; it never actually generates a reply."""

    def __init__(self) -> None:
        super().__init__(instructions="You are a placeholder agent used only to test Rime TTS output.")


async def entrypoint(ctx: JobContext) -> None:
    logger.info("[VOICE] SESSION_CONNECTING")
    await ctx.connect()

    session = AgentSession(
        tts=rime.TTS(
            model=RIME_MODEL,
            speaker=RIME_SPEAKER,
            reduce_latency=True,
        ),
    )

    logger.info("[VOICE] SESSION_STARTING")
    await session.start(room=ctx.room, agent=GreeterOnly())

    logger.info("[VOICE] RIME_SPEAK generation=STEP3_HARDCODED")
    await session.say(
        "DHWANI voice runtime step three online. This is real Rime audio, not a placeholder.",
        allow_interruptions=False,
    )
    logger.info("[VOICE] RIME_SPEAK_COMPLETE")


# --- Entrypoint wiring: this is the part flagged as version-sensitive above ---
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
