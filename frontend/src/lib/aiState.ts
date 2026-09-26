import type { AIState } from '../api/emails';

/**
 * One description of the local-AI state machine, shared by every surface that
 * reports it. The vocabulary used to live in five places with five different
 * wordings, which is how a header and a settings page end up disagreeing about
 * whether the same state is "Ready", "AI ready" or "Local AI is offline".
 *
 * `AIState` is the backend's own union (app.ai.supervisor), so an unknown value
 * is a genuine anomaly rather than something to render as fact.
 */
export type AiTone = 'ok' | 'working' | 'warning' | 'danger';

export type AiStateMeta = {
  /** Short form for a chip or rail row. */
  chip: string;
  /** Single word for a settings value column. */
  word: string;
  /** Tooltip / supporting sentence. */
  hint: string;
  /** Full sentence for prose. */
  sentence: string;
  tone: AiTone;
  /** Whether a retry action is meaningful in this state. */
  retryable: boolean;
  /** False when the value was not part of the known state machine. */
  known: boolean;
};

const META: Record<AIState, Omit<AiStateMeta, 'known'>> = {
  ready: {
    chip: 'AI ready',
    word: 'Ready',
    hint: 'Local AI is ready',
    sentence: 'Local AI is ready.',
    tone: 'ok',
    retryable: false,
  },
  initializing: {
    chip: 'AI starting',
    word: 'Starting',
    hint: 'Local AI is starting',
    sentence: 'Local AI is starting.',
    tone: 'working',
    retryable: false,
  },
  ollama_not_running: {
    chip: 'AI offline',
    word: "Ollama isn't running",
    hint: "Ollama is not running. Your mailbox works; summaries resume when it is.",
    sentence: 'Local AI is offline.',
    tone: 'danger',
    retryable: true,
  },
  model_missing: {
    chip: 'Model missing',
    word: 'Model missing',
    hint: 'The local model is not installed. Choose one in Settings.',
    sentence: 'The local model is not installed.',
    tone: 'danger',
    retryable: true,
  },
  temporarily_unavailable: {
    chip: 'AI busy',
    word: 'Temporarily unavailable',
    hint: 'Local AI is busy',
    sentence: 'Local AI is temporarily unavailable.',
    tone: 'warning',
    retryable: true,
  },
  recovering: {
    chip: 'AI recovering',
    word: 'Recovering',
    hint: 'Local AI is recovering',
    sentence: 'Local AI is recovering.',
    tone: 'working',
    retryable: true,
  },
  error: {
    chip: 'AI error',
    word: 'Error',
    hint: 'Local AI reported an error',
    sentence: 'Local AI reported an error.',
    tone: 'danger',
    retryable: true,
  },
};

const UNKNOWN: Omit<AiStateMeta, 'known'> = {
  chip: 'AI starting',
  word: 'Starting',
  hint: 'Local AI status is not recognised',
  sentence: 'Local AI is starting.',
  tone: 'working',
  retryable: false,
};

/** Never throws and never invents a state: an unrecognised value is reported as such. */
export function aiStateMeta(state: string | null | undefined): AiStateMeta {
  if (state && state in META) {
    return { ...META[state as AIState], known: true };
  }
  return { ...UNKNOWN, known: false };
}
