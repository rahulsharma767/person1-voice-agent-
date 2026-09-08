import logging
import os

from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import google, rime


# ---------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------

load_dotenv()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("dhwani")


# ---------------------------------------------------------
# DHWANI AGENT
# ---------------------------------------------------------

class DhwaniAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are DHWANI, a natural voice assistant. "
                "Listen carefully to the user and respond clearly and concisely. "
                "Keep spoken responses short, natural, and conversational. "
                "Do not mention internal systems, APIs, models, or implementation details."
            )
        )


# ---------------------------------------------------------
# LIVEKIT ENTRYPOINT
# ---------------------------------------------------------

async def entrypoint(ctx: JobContext):

    logger.info("[DHWANI] Connecting to LiveKit...")

    await ctx.connect()


    # -----------------------------------------------------
    # GEMINI TEXT LLM
    # -----------------------------------------------------

    logger.info("[DHWANI] Creating Gemini 3.5 Flash Lite...")

    llm = google.LLM(
        model="gemini-3.5-flash-lite",
        api_key=os.getenv("GOOGLE_API_KEY"),
    )


    # -----------------------------------------------------
    # RIME TTS
    # -----------------------------------------------------

    logger.info("[DHWANI] Creating Rime TTS...")

    tts = rime.TTS(
        model="mist",
        speaker="rainforest",
        reduce_latency=True,
    )


    # -----------------------------------------------------
    # AGENT SESSION
    # -----------------------------------------------------

    logger.info("[DHWANI] Creating AgentSession...")

    session = AgentSession(
        llm=llm,
        tts=tts,
    )


    # -----------------------------------------------------
    # START SESSION
    # -----------------------------------------------------

    logger.info("[DHWANI] Starting session...")

    await session.start(
        room=ctx.room,
        agent=DhwaniAgent(),
    )


    logger.info("[DHWANI] SESSION_READY")
    logger.info("[DHWANI] Speak into the microphone.")


# ---------------------------------------------------------
# START APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )