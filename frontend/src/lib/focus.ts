import { createContext, useCallback, useContext } from 'react';

/**
 * Focus moves only when the user's own action invalidates what they were on.
 * A background refetch, a poll, or a re-render must never move it.
 *
 * That rule is easy to state and easy to break by accident, so navigation
 * intent is recorded explicitly rather than inferred. A component that
 * deliberately replaces the user's context calls `requestFocus`; the shell
 * consumes that intent once. Nothing infers intent from a state change, which
 * is what makes "typing a global search does not yank focus to the page
 * heading" true by construction rather than by luck.
 */
export type FocusTarget = 'view' | 'reader';

export type FocusIntent = {
  /** Record that the next view change should move focus. */
  requestFocus: (target: FocusTarget) => void;
  /**
   * Take the recorded intent, but only for the target that asked for it.
   * Returns false when there is no intent, or it belongs to the other target —
   * so a view change cannot swallow a pending reader focus.
   */
  takeFocusIntent: (target: FocusTarget) => boolean;
};

const noop: FocusIntent = {
  requestFocus: () => {},
  takeFocusIntent: () => false,
};

export const FocusIntentContext = createContext<FocusIntent>(noop);

export function useFocusIntent(): FocusIntent {
  return useContext(FocusIntentContext);
}

/**
 * Focus without letting a pointer click light up a focus ring. `:focus-visible`
 * already suppresses the ring for mouse users in supporting browsers; guarding
 * the call keeps behaviour identical where it is not supported.
 */
export function focusTarget(node: HTMLElement | null | undefined): void {
  if (!node) return;
  if (typeof node.focus === 'function') node.focus();
}

/** True when `node` is still in the document, so a stale ref cannot steal focus. */
export function isAttached(node: HTMLElement | null | undefined): node is HTMLElement {
  return Boolean(node && node.isConnected);
}

/**
 * A retry that re-homes focus only when it actually worked.
 *
 * The button the user pressed lives inside the error block, so a successful
 * retry unmounts the very element that had focus and leaves the user stranded
 * on <body> with nothing to Tab from. Moving focus on every retry would be
 * worse: on a persistent failure the error is still there and the button is
 * still the right place to be. So the refetch is awaited and the result checked.
 */
export function useRetryPreservingFocus(
  refetch: () => Promise<unknown>
): () => void {
  const { requestFocus } = useFocusIntent();
  return useCallback(() => {
    void Promise.resolve()
      .then(() => refetch())
      .then((result) => {
        const failed =
          typeof result === 'object' &&
          result !== null &&
          'isError' in result &&
          (result as { isError?: boolean }).isError === true;
        if (!failed) requestFocus('view');
      })
      .catch(() => {
        // A rejected refetch is a failed retry; leave focus where it is.
      });
  }, [refetch, requestFocus]);
}
