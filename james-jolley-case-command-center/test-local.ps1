$payload = Get-Content "tests\test_payload.json" -Raw

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/api/case-update" `
  -Method POST `
  -ContentType "application/json" `
  -Body $payload | ConvertTo-Json -Depth 20
