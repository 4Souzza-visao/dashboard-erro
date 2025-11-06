#!/bin/bash

# Script de teste da API do Error Dashboard

API_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================================"
echo "  TESTANDO API DO ERROR DASHBOARD"
echo "======================================================"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
response=$(curl -s -w "\n%{http_code}" $API_URL/health)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - API está online"
    echo "Response: $body"
else
    echo -e "${RED}✗ FAILED${NC} - API não está acessível (HTTP $http_code)"
fi
echo ""

# Test 2: Create Error
echo -e "${YELLOW}Test 2: Criar um erro${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST $API_URL/api/errors \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test error from script",
    "error_type": "APPLICATION",
    "severity": "LOW",
    "source": "test_script"
  }')
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" -eq 201 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Erro criado com sucesso"
    error_id=$(echo "$response" | head -n-1 | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo "Error ID: $error_id"
else
    echo -e "${RED}✗ FAILED${NC} - Falha ao criar erro (HTTP $http_code)"
fi
echo ""

# Test 3: List Errors
echo -e "${YELLOW}Test 3: Listar erros${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/errors?limit=5")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Lista obtida com sucesso"
    total=$(echo "$response" | head -n-1 | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
    echo "Total de erros: $total"
else
    echo -e "${RED}✗ FAILED${NC} - Falha ao listar erros (HTTP $http_code)"
fi
echo ""

# Test 4: Get Statistics
echo -e "${YELLOW}Test 4: Obter estatísticas${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/stats/summary?days=7")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} - Estatísticas obtidas com sucesso"
else
    echo -e "${RED}✗ FAILED${NC} - Falha ao obter estatísticas (HTTP $http_code)"
fi
echo ""

# Test 5: Update Error (se temos um error_id)
if [ ! -z "$error_id" ]; then
    echo -e "${YELLOW}Test 5: Atualizar erro #$error_id${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$API_URL/api/errors/$error_id" \
      -H "Content-Type: application/json" \
      -d '{
        "status": "RESOLVED",
        "notes": "Test completed"
      }')
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ PASSED${NC} - Erro atualizado com sucesso"
    else
        echo -e "${RED}✗ FAILED${NC} - Falha ao atualizar erro (HTTP $http_code)"
    fi
    echo ""
fi

echo "======================================================"
echo "  TESTES CONCLUÍDOS"
echo "======================================================"
echo ""
echo "Dashboard: http://localhost:3000"
echo "API Docs: $API_URL/docs"

