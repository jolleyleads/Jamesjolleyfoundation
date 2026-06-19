$RenderUrl = Read-Host "Paste your Render URL, example https://james-jolley-case-command-center.onrender.com"

$payload = Get-Content "tests\test_payload.json" -Raw

Invoke-RestMethod `
  -Uri "$RenderUrl/api/case-update" `
  -Method POST `
  -ContentType "application/json" `
  -Body $payload | ConvertTo-Json -Depth 20
