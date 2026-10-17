# CONTEXT_RULES — transposição da Fase 1
Python 3.11+; type hints em todas as funções e parâmetros; SRP e PEP 8;
Google style docstrings; funções pequenas e coesas; exceções específicas;
logs estruturados via logging; nomes descritivos e código manutenível.
Não usar bibliotecas externas não autorizadas. Runtime: apenas biblioteca padrão.
Testes: pytest autorizado. Não alterar/remover cenários de aceite, não modificar a
estrutura planejada, não persistir dados de tarefas em arquivos/bancos, não mudar
assinaturas públicas sem autorização, não gerar funcionalidade sem testes, não
inserir duplicação e não assumir comportamentos ausentes do contrato.
Fornecer contexto completo à IA; verificar entendimento antes da geração;
solicitar justificativas, revisar criticamente e corrigir violações.
Contrato público: analyze_tasks(tasks: list[dict[str, object]]) -> dict[str, object]
e exceção TaskValidationError(ValueError).
A Fase 2 atualiza a Fase 1: vazio/sem concluídas retornam 0.0, sem divisão por zero.
A revisão e homologação humana final são pendentes até execução pelo estudante.
