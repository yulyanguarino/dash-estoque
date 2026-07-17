# 📊 Dashboard Executivo de Estoque — Tidimar Hospitalar

## 📋 Visão Geral

Dashboard executivo moderno desenvolvido em **Streamlit** para monitoramento em tempo real de operações de separação e conferência de pedidos. Interface dark elegante com inspiração em dashboards premium (Power BI, Grafana), oferecendo visualizações interativas e KPIs centralizados.

**Funcionalidades principais:**
- 4 KPIs executivos com sparklines de tendência
- Análise de produção por separador (gráficos de barras e pizza)
- Análise de produção por conferente (gráficos de barras e pizza)
- Filtros dinâmicos (mês, separador, conferente)
- Exportação de dados em CSV
- Deploy gratuito via Streamlit Community Cloud

---

## 🏗️ Arquitetura do Projeto

```
dash estoque/
├── main.py                      # Interface Streamlit (layout, filtros, gráficos)
├── data_processing.py           # Funções de limpeza e agregação de dados
├── requirements.txt             # Dependências Python
├── README.md                    # Esta documentação
└── BASE_Dashboard.xlsx          # Arquivo de dados (não comitar em prod se sensível)
```

### 📄 main.py
**Responsabilidade:** Interface do usuário, interatividade e visualizações

- Configuração da página Streamlit (layout wide, tema dark)
- Estilos customizados via CSS (cards arredondados, sombras, cores corporativas)
- Upload de arquivo com validação
- Filtros dinâmicos (sidebar)
- 4 cards de KPI com sparklines
- Seção de Separação (barras + pizza)
- Seção de Conferência (barras + pizza)
- Tabela de dados brutos (expandível) com download
- Todos os gráficos usam Plotly `template='plotly_dark'`

### 📊 data_processing.py
**Responsabilidade:** ETL (Extract, Transform, Load) — limpeza e agregação de dados

**Funções principais:**
- `load_excel(uploaded_file)` → valida aba 'BASE', retorna DataFrame
- `sanitize_columns(df)` → remove espaços extras nos nomes de colunas
- `remove_totais(df)` → filtra linhas de subtotal/total
- `coerce_quantidades(df)` → força colunas de QTD para int (trata malformados com NaN → 0)
- `parse_datas(df)` → expande coluna DATA em MES_NUM, MES_NOME (PT-BR), ANO
- `preprocess(uploaded_file)` → orquestra pipeline completo de limpeza
- `get_kpis(df)` → calcula 4 KPIs (pedidos, separados, conferidos, equipe)
- `producao_por_separador(df)` → agrega por SEPARADOR
- `producao_por_conferente(df)` → agrega por CONFERENTE
- `serie_mensal(df, coluna_qtd)` → série temporal por mês (para sparklines)

Todas as funções têm docstrings explicando parâmetros, retornos e comportamento.

---

## 🎨 Design e Tema

### Paleta de Cores
- **Verde corporativo:** `#76C043` — barras de separação, indicators de separação
- **Azul/Verde escuro:** `#005F5F` — barras de conferência, indicators de conferência
- **Azul claro:** `#58a6ff` — KPI geral (pedidos, equipe)
- **Fundo dark:** `#0e1117` (GitHub dark mode) — base neutra e profissional

### Componentes
- **Cards de KPI:** fundo gradiente escuro, borda esquerda colorida (4px), sombra sutil, texto grande (2.5rem)
- **Gráficos Plotly:** todos com `template='plotly_dark'`, margem padronizada, hover interativo
- **Filtros:** sidebar limpo com multiselect (Todos, individual, múltiplos)
- **Responsividade:** CSS media queries para mobile (breakpoint 768px)

---

## 🚀 Como Rodar Localmente

### 1. Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### 2. Clonar ou preparar projeto
```bash
cd "C:\Users\Tidimar\Desktop\dash estoque"
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Rodar o dashboard
```bash
streamlit run main.py
```

O Streamlit abrirá automaticamente `http://localhost:8501` no navegador.

### 5. Usar o dashboard
1. Clique em **"Carregar planilha"** no painel esquerdo (sidebar)
2. Selecione o arquivo `BASE_Dashboard.xlsx`
3. Aguarde processamento (validação, limpeza, agregação)
4. Use filtros para explorar dados específicos
5. Examine KPIs, gráficos, e tabela de dados
6. (Opcional) Baixe dados filtrados em CSV via botão na seção expandível

---

## 📤 Deploy Gratuito via Streamlit Community Cloud

### Passo 1: Preparar repositório GitHub
1. Crie uma conta em [github.com](https://github.com) (se ainda não tiver)
2. Crie um novo repositório público chamado `dash-estoque`
3. Clone localmente:
   ```bash
   git clone https://github.com/seu-usuario/dash-estoque.git
   cd dash-estoque
   ```

### Passo 2: Copiar arquivos do projeto
Copie para o repositório:
- `main.py`
- `data_processing.py`
- `requirements.txt`
- `.gitignore` (criar arquivo contendo):
  ```
  *.xlsx
  *.xls
  __pycache__/
  *.pyc
  .env
  venv/
  ```

**Nota:** Não commite o arquivo `.xlsx` se contiver dados sensíveis. O usuário final fará upload via interface.

### Passo 3: Commit e push
```bash
git add .
git commit -m "Initial commit: Dashboard Tidimar"
git push -u origin main
```

### Passo 4: Deploy no Streamlit Community Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta GitHub
3. Clique **"New app"** → selecione seu repositório `dash-estoque` → branch `main` → arquivo `main.py`
4. Clique **"Deploy"**
5. Aguarde (pode levar 2-3 minutos na primeira vez)
6. Seu dashboard estará disponível em `https://seu-usuario-dash-estoque.streamlit.app`

### Passo 5: Compartilhar
Compartilhe o link com colegas. Eles podem:
- Acessar direto (sem instalar nada)
- Fazer upload do arquivo `BASE_Dashboard.xlsx`
- Usar filtros e exportar dados

---

## 🔧 Customizações Comuns

### Alterar cores corporativas
Editar `main.py`, procurar por `#76C043` ou `#005F5F` e substituir por cores desejadas.

### Adicionar nova métrica ao KPI
1. Editar `data_processing.py` → função `get_kpis()`
2. Adicionar cálculo (ex: `'taxa_conferencia': ...`)
3. Editar `main.py` → adicionar nova coluna em `st.columns()` com card e sparkline

### Adicionar filtro novo
1. Editar `main.py` → sidebar (seção "Filtros")
2. Criar novo `st.multiselect()` ou `st.selectbox()`
3. Aplicar filtro no DataFrame: `df_filtrado = df_filtrado[df_filtrado['COLUNA'].isin([...)]`

### Modificar estrutura de gráficos
Todos os gráficos usam Plotly Express (`px.bar`, `px.pie`). Documentação: [plotly.com/python](https://plotly.com/python)

---

## ⚠️ Troubleshooting

### "Aba 'BASE' não encontrada"
- Verifique se o arquivo Excel contém uma aba nomeada exatamente `BASE`
- Nomes sensíveis a maiúsculas/minúsculas

### "Erro ao carregar arquivo"
- Confirme formato: `.xlsx` ou `.xls`
- Arquivo não está corrompido
- Verificar se arquivo não está aberto em outro programa

### Gráficos não renderizam
- Confirmar que `plotly` está instalado: `pip install --upgrade plotly`
- Limpar cache Streamlit: `streamlit cache clear`

### Valores de KPI estranhos
- Verificar coluna QTD: erros de coerção são reportados (ℹ️ no sidebar)
- Confirmar que dados não têm subtotais que não foram removidos

---

## 📝 Licença e Créditos

Desenvolvido como dashboard executivo moderno para **Tidimar Hospitalar**.

**Stack tecnológico:**
- Streamlit — framework web Python
- Pandas — manipulação de dados
- Plotly — visualizações interativas
- openpyxl — leitura de Excel

---

## 📧 Suporte

Para dúvidas, bugs ou sugestões:
1. Verifique a seção **Troubleshooting** acima
2. Consulte a documentação:
   - [Streamlit Docs](https://docs.streamlit.io)
   - [Plotly Python](https://plotly.com/python)
   - [Pandas Docs](https://pandas.pydata.org/docs)

---

**Versão:** 1.0  
**Última atualização:** 2026-07-02  
**Mantido por:** Tidimar Hospitalar — Time de TI
