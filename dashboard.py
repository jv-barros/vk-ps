import streamlit as st
import pandas as pd

# Step 1: Load all the datasets / Carregar todos os datasets
@st.cache_data
def load_data():
    # Step 1.1: Define file paths / Definir caminhos dos arquivos
    utm_path = 'TabelaPesquisaUTMsn - TabelaPesquisaUTMsn.csv'
    vendas_path = 'TabelaVendas.csv'
    pesquisa_path = 'TabelaPesquisa.csv'
    ads_path = 'TabelaAdsLinks.csv'
    
    # Step 1.2: Load CSV files into dataframes / Carregar arquivos CSV em dataframes
    utm_df = pd.read_csv(utm_path)
    vendas_df = pd.read_csv(vendas_path)
    pesquisa_df = pd.read_csv(pesquisa_path)
    ads_df = pd.read_csv(ads_path)

    # Step 1.3: Clean data - keep relevant columns and remove duplicates
    # Limpeza dos dados - manter colunas relevantes e remover duplicatas
    utm_df_clean = utm_df[['email', 'utmsource', 'utmterm', 'utmmedium']].drop_duplicates()
    vendas_df_clean = vendas_df[['email']].drop_duplicates()
    pesquisa_df_clean = pesquisa_df[['email', 'idade', 'renda', 'tempo_me_conhece']].drop_duplicates()
    ads_df_clean = ads_df[['utmterm', 'instagram_permalink_url']].drop_duplicates()

    # Step 1.4: Merge UTM and persona survey data on 'email'
    # Mesclar dados de UTM e pesquisa de persona com base no 'email'
    merged_df = pd.merge(utm_df_clean, pesquisa_df_clean, on='email', how='left')

    # Step 1.5: Merge sales data and add 'purchase_status' column (1 for buyers, 0 for non-buyers)
    # Mesclar dados de vendas e adicionar coluna 'purchase_status' (1 para compradores, 0 para não-compradores)
    merged_df = pd.merge(merged_df, vendas_df_clean, on='email', how='left', indicator='purchase_status')
    merged_df['purchase_status'] = merged_df['purchase_status'].apply(lambda x: 1 if x == 'both' else 0)
    
    # Step 1.6: Merge ads data with UTM data using 'utmterm'
    # Mesclar dados de anúncios com base no 'utmterm'
    final_df = pd.merge(merged_df, ads_df_clean, on='utmterm', how='left')
    
    return final_df

# Step 2: Load data into the app / Carregar os dados no aplicativo
df = load_data()

# Step 3: Create dashboard title / Criar título do painel
st.title('Painel de Insights de Lançamento')

# Step 4: Show summary statistics / Exibir estatísticas resumidas
st.header('Estatísticas Resumidas')
st.write(f"**Total Leads:** {df['email'].nunique()}")  # Step 4.1: Total number of leads / Total de leads
st.write(f"**Total Buyers:** {df[df['purchase_status'] == 1]['email'].nunique()}")  # Step 4.2: Total buyers / Total de compradores
st.write(f"**Conversion Rate:** {round(df['purchase_status'].mean() * 100, 2)}%")  # Step 4.3: Conversion rate / Taxa de conversão

# Step 5: Create filtering options in sidebar / Criar opções de filtragem na barra lateral
st.sidebar.header('Filtrar por Fonte UTM')
utm_source_filter = st.sidebar.multiselect(
    'Selecionar Fonte UTM', options=df['utmsource'].unique(), default=df['utmsource'].unique())

st.sidebar.header('Filtrar por Termo UTM')
utm_term_filter = st.sidebar.multiselect(
    'Selecionar Termo UTM', options=df['utmterm'].unique(), default=df['utmterm'].unique())

# Step 6: Filter data based on sidebar selections / Filtrar dados com base nas seleções da barra lateral
filtered_df = df[(df['utmsource'].isin(utm_source_filter)) & (df['utmterm'].isin(utm_term_filter))]

# Step 7: Display filtered data / Exibir dados filtrados
st.header('Dados Filtrados')
st.write(filtered_df)

# Step 8: Show conversion rate by UTM Source / Exibir taxa de conversão por Fonte UTM
st.header('Taxa de Conversão por Fonte UTM')
conversion_rate_by_source = filtered_df.groupby('utmsource')['purchase_status'].mean().reset_index()
conversion_rate_by_source.set_index('utmsource', inplace=True)

# Improved visualization for conversion rates
st.bar_chart(conversion_rate_by_source['purchase_status'], use_container_width=True)  # Step 8.1: Display conversion rates in a bar chart / Exibir taxas de conversão em um gráfico de barras

# Insight
st.markdown("---")
st.write("A maior taxa de conversão por fonte UTM é pelo youtube.")


# Step 9: Display Instagram Ads Links / Exibir links dos anúncios no Instagram
st.header('Anúncios no Instagram')
st.write('Abaixo estão os anúncios vinculados aos termos UTM selecionados:')  # Anúncios vinculados aos UTM Terms selecionados
ads = filtered_df[['utmterm', 'instagram_permalink_url']].drop_duplicates()  # Step 9.1: Show unique ad links / Exibir links de anúncios únicos

# Improved display for ad links
if not ads.empty:
    st.write(ads)
else:
    st.write("Nenhum anúncio encontrado para os termos UTM selecionados.")  # Handling empty data gracefully

# Optional: Add a footer for additional context / Rodapé para contexto adicional
st.markdown("---")
st.write("Esta análise oferece insights sobre a eficácia das fontes UTM e anúncios no Instagram para o lançamento do produto.")

