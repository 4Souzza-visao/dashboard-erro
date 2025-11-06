# Script de teste da API do Error Dashboard (PowerShell)

$API_URL = "http://localhost:8000"

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  TESTANDO API DO ERROR DASHBOARD" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/health" -Method GET
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ PASSED - API está online" -ForegroundColor Green
        Write-Host "Response: $($response.Content)"
    }
} catch {
    Write-Host "✗ FAILED - API não está acessível" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
Write-Host ""

# Test 2: Create Error
Write-Host "Test 2: Criar um erro" -ForegroundColor Yellow
try {
    $body = @{
        message = "Test error from PowerShell script"
        error_type = "APPLICATION"
        severity = "LOW"
        source = "test_script"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "$API_URL/api/errors" -Method POST -Body $body -ContentType "application/json"
    
    if ($response.StatusCode -eq 201) {
        Write-Host "✓ PASSED - Erro criado com sucesso" -ForegroundColor Green
        $error_id = ($response.Content | ConvertFrom-Json).id
        Write-Host "Error ID: $error_id"
    }
} catch {
    Write-Host "✗ FAILED - Falha ao criar erro" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
Write-Host ""

# Test 3: List Errors
Write-Host "Test 3: Listar erros" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/api/errors?limit=5" -Method GET
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ PASSED - Lista obtida com sucesso" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host "Total de erros: $($data.total)"
    }
} catch {
    Write-Host "✗ FAILED - Falha ao listar erros" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
Write-Host ""

# Test 4: Get Statistics
Write-Host "Test 4: Obter estatísticas" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$API_URL/api/stats/summary?days=7" -Method GET
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ PASSED - Estatísticas obtidas com sucesso" -ForegroundColor Green
        $stats = $response.Content | ConvertFrom-Json
        Write-Host "Total de erros (7 dias): $($stats.total_errors)"
    }
} catch {
    Write-Host "✗ FAILED - Falha ao obter estatísticas" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
Write-Host ""

# Test 5: Update Error
if ($error_id) {
    Write-Host "Test 5: Atualizar erro #$error_id" -ForegroundColor Yellow
    try {
        $body = @{
            status = "RESOLVED"
            notes = "Test completed"
        } | ConvertTo-Json

        $response = Invoke-WebRequest -Uri "$API_URL/api/errors/$error_id" -Method PATCH -Body $body -ContentType "application/json"
        
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ PASSED - Erro atualizado com sucesso" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ FAILED - Falha ao atualizar erro" -ForegroundColor Red
        Write-Host $_.Exception.Message
    }
    Write-Host ""
}

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  TESTES CONCLUÍDOS" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard: http://localhost:3000"
Write-Host "API Docs: $API_URL/docs"

