!macro NSIS_HOOK_POSTINSTALL
  ; Tauri's default NSIS update path skips shortcut creation when a shortcut
  ; already exists and the main binary name did not change. Recreate Alfred
  ; shortcuts on every install/update so stale absolute targets from another
  ; user profile cannot survive into a current-user install.
  SetOutPath "$INSTDIR"

  Delete "$SMPROGRAMS\${PRODUCTNAME}.lnk"

  !if "${STARTMENUFOLDER}" != ""
    Delete "$SMPROGRAMS\$AppStartMenuFolder\${PRODUCTNAME}.lnk"
    CreateDirectory "$SMPROGRAMS\$AppStartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$AppStartMenuFolder\${PRODUCTNAME}.lnk" "$INSTDIR\${MAINBINARYNAME}.exe"
    !insertmacro SetShortcutTarget "$SMPROGRAMS\$AppStartMenuFolder\${PRODUCTNAME}.lnk" "$INSTDIR\${MAINBINARYNAME}.exe"
    !insertmacro SetLnkAppUserModelId "$SMPROGRAMS\$AppStartMenuFolder\${PRODUCTNAME}.lnk"
  !else
    CreateShortcut "$SMPROGRAMS\${PRODUCTNAME}.lnk" "$INSTDIR\${MAINBINARYNAME}.exe"
    !insertmacro SetShortcutTarget "$SMPROGRAMS\${PRODUCTNAME}.lnk" "$INSTDIR\${MAINBINARYNAME}.exe"
    !insertmacro SetLnkAppUserModelId "$SMPROGRAMS\${PRODUCTNAME}.lnk"
  !endif

  Delete "$DESKTOP\${PRODUCTNAME}.lnk"
  CreateShortcut "$DESKTOP\${PRODUCTNAME}.lnk" "$INSTDIR\${MAINBINARYNAME}.exe"
  !insertmacro SetShortcutTarget "$DESKTOP\${PRODUCTNAME}.lnk" "$INSTDIR\${MAINBINARYNAME}.exe"
  !insertmacro SetLnkAppUserModelId "$DESKTOP\${PRODUCTNAME}.lnk"

  ; In some automated/elevated current-user installs, NSIS shell-folder
  ; variables can resolve differently from the user's environment-backed
  ; Start Menu location. Also repair the environment-resolved current-user
  ; shortcuts to the environment-resolved local install directory.
  ReadEnvStr $R8 "APPDATA"
  ReadEnvStr $R9 "LOCALAPPDATA"
  ${If} $R8 != ""
  ${AndIf} $R9 != ""
    Delete "$R8\Microsoft\Windows\Start Menu\Programs\${PRODUCTNAME}.lnk"
    CreateShortcut "$R8\Microsoft\Windows\Start Menu\Programs\${PRODUCTNAME}.lnk" "$R9\${PRODUCTNAME}\${MAINBINARYNAME}.exe"
    !insertmacro SetShortcutTarget "$R8\Microsoft\Windows\Start Menu\Programs\${PRODUCTNAME}.lnk" "$R9\${PRODUCTNAME}\${MAINBINARYNAME}.exe"
    !insertmacro SetLnkAppUserModelId "$R8\Microsoft\Windows\Start Menu\Programs\${PRODUCTNAME}.lnk"
  ${EndIf}

  ReadEnvStr $R8 "USERPROFILE"
  ReadEnvStr $R9 "LOCALAPPDATA"
  ${If} $R8 != ""
  ${AndIf} $R9 != ""
    Delete "$R8\Desktop\${PRODUCTNAME}.lnk"
    CreateShortcut "$R8\Desktop\${PRODUCTNAME}.lnk" "$R9\${PRODUCTNAME}\${MAINBINARYNAME}.exe"
    !insertmacro SetShortcutTarget "$R8\Desktop\${PRODUCTNAME}.lnk" "$R9\${PRODUCTNAME}\${MAINBINARYNAME}.exe"
    !insertmacro SetLnkAppUserModelId "$R8\Desktop\${PRODUCTNAME}.lnk"
  ${EndIf}
!macroend
