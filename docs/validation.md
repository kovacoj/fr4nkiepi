# Validation

See `reports/validation.md` for command evidence. The live Pages endpoint and its summary feed returned HTTP 200 after GitHub reported the deployment built successfully.

Current automated coverage includes registry lifecycle, activation denial, permission denial, dependency composition, fresh-process reuse, MCP protocol calls, qualification scoring, idempotent telemetry ingestion, phase-separated cost aggregation, unknown costs, privacy rejection, Pages-tree isolation, and system sampling.

Live Discord, provider usage, reboot recovery, and automated Pi publication remain unverified and must not be described as passing.

## Discord And Speech Configuration

- Discord REST bot authentication returned HTTP 200.
- Hermes Discord optional dependency installed through `hermes pm install --extra discord`.
- Gateway foreground process was detected by an independent `hermes gateway status` call.
- `hermes-gateway.service` is installed, enabled, active, and running as the unprivileged runtime account.
- Systemd lingering is enabled, so the user gateway survives SSH logout.
- ElevenLabs authentication returned HTTP 200.
- STT is configured for ElevenLabs `scribe_v2`.
- TTS is configured for ElevenLabs `eleven_flash_v2_5` with Hermes' default voice.
- Text Discord transport is ready for an operator message test.

System Opus is installed and visible to the ARM64 linker. After gateway restart, the prior `Opus codec not found` warning was absent. Voice-channel playback dependencies are therefore ready, but voice join, transcription, synthesis, multi-user behavior, and spoken playback still require operator testing in Discord.

Not passed: the configured OpenRouter model has no provider credential, so model responses cannot be claimed.
