# Como publicar este projeto no GitHub

## Preparação
- Crie uma conta no GitHub (se ainda não tiver).
- Instale o Git: https://git-scm.com/downloads

## Passo a passo
1. Inicialize o repositório local:
   - `git init`
   - `git add .`
   - `git commit -m "Inicializa projeto Pisk & Click"`

2. Crie o repositório remoto no GitHub:
   - Acesse GitHub e clique em “New”.
   - Nome sugerido: `pisk-and-click`.
   - Não adicione arquivos iniciais (README/.gitignore), usaremos os locais.

3. Conecte e envie:
   - `git remote add origin https://github.com/<seu-usuario>/pisk-and-click.git`
   - `git branch -M main`
   - `git push -u origin main`

4. Boas práticas
   - Mantenha `requirements.txt` atualizado.
   - Suba apenas arquivos necessários (instaladores grandes já estão no `.gitignore`).
   - Use `Docs/` para manuais, guias e changelog.
   - Crie `releases` para versões empacotadas.

## Publicação de novas versões
- `git pull` para sincronizar.
- `git add` dos arquivos alterados.
- `git commit -m "Descrição clara da alteração"`.
- `git tag vX.Y.Z` (opcional para marcação de versão).
- `git push && git push --tags`.

## Estrutura recomendada para GitHub
```
assets/      # Logos e ícones
Docs/        # Documentação
profiles/    # Perfis de usuário
*.py         # Fontes do aplicativo
README.md    # Documentação principal
requirements.txt
.gitignore
```