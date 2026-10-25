# Context Rules & AI Governance - TaskAnalyzer

## Diretrizes Arquiteturais Obrigatórias
1. Python 3.11+ como versão mínima do runtime.
2. Type Hints obrigatórios em 100% das funções, métodos e parâmetros.
3. Tratamento rigoroso de exceções do domínio (TaskValidationError).
4. Código limpo, modular e aderente ao PEP 8.
5. Observabilidade via logging estruturado (módulo nativo logging).

## Proibições Explícitas
1. PROIBIDO utilizar bibliotecas externas não autorizadas (ex.: pandas, numpy). Usar apenas biblioteca padrão Python.
2. PROIBIDO alterar as assinaturas das funções públicas e nomes de exceções contratuais.
3. PROIBIDO persistir dados em disco ou conectar a bancos de dados externos.
4. PROIBIDO suprimir avisos ou afrouxar os testes da suíte pytest.