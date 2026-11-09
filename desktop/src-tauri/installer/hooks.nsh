; Alfred NSIS installer hooks -- makes the uninstaller's "delete my data"
; choice real. Registered via bundle.windows.nsis.installerHooks.
;
; THE DEFECT THIS FIXES
;
; Tauri's uninstall template wipes "$LOCALAPPDATA\${BUNDLEID}", which for
; Alfred is %LOCALAPPDATA%\com.alfred.local -- a directory that has never
; existed. Alfred's data lives at %LOCALAPPDATA%\AlfredData and, on installs
; that predate ADR-012, beside the binaries in the install directory itself.
; So the checkbox deleted nothing: a user who asked for their mail to be
; removed kept all of it. See ADR-012 and docs/Memory.md finding 6.
;
; WHAT IS DELETED, AND ONLY WHEN
;
; Only when the user ticked the checkbox on the uninstall confirmation page
; AND this is not an upgrade. Both guards matter:
;
;   $DeleteAppDataCheckboxState  is set in un.ConfirmLeave, so it is "" (0)
;                                unless the page was shown and the box
;                                ticked. A silent uninstall therefore never
;                                deletes data -- the safe default.
;   $UpdateMode                  is 1 when the installer is replacing this
;                                version, where the old uninstaller runs to
;                                clear binaries, not user data.
;
; NEVER touched here:
;   %LOCALAPPDATA%\Ollama\models  -- Ollama's model store, not Alfred's data,
;                                   and shared with every other Ollama
;                                   client on the machine.
;   anything outside AlfredData and the install directory.

!ifndef ALFRED_DATA_DIR
  !define ALFRED_DATA_DIR "$LOCALAPPDATA\AlfredData"
!endif

; Exposed as its own macro so tools/release/test_installer_hooks.py can
; compile and execute exactly this code against a temporary directory,
; overriding ALFRED_DATA_DIR. The deletion logic is therefore tested, not
; only reviewed.
!macro AlfredDeleteUserData
  DetailPrint "Deleting Alfred user data"

  ; The mailbox, its WAL/SHM sidecars, the logs, and any backup kept
  ; alongside them.
  RMDir /r "${ALFRED_DATA_DIR}"

  ; Legacy layout: data that still sits beside the binaries because it
  ; predates ADR-012 and the app has not had a clean start since.
  Delete "$INSTDIR\alfred.sqlite3"
  Delete "$INSTDIR\alfred.sqlite3-wal"
  Delete "$INSTDIR\alfred.sqlite3-shm"
  Delete "$INSTDIR\alfred.sqlite3*.bak"

  ; Succeeds only once nothing of the user's is left in it.
  RMDir "$INSTDIR"
!macroend

!macro NSIS_HOOK_POSTUNINSTALL
  ; The template's own branch has already run by this point and removed the
  ; registry keys; it just aimed its RMDir at the wrong directory.
  SetShellVarContext current
  ${If} $DeleteAppDataCheckboxState = 1
  ${AndIf} $UpdateMode <> 1
    !insertmacro AlfredDeleteUserData
  ${Else}
    DetailPrint "Keeping Alfred user data"
  ${EndIf}
!macroend
