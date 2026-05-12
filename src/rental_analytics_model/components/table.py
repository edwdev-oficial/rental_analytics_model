import streamlit as st

# def personal_table(df):

#     html = df.to_html(index=False, border=0)

#     st.markdown("""
#     <style>
#     .tabela-clean table {
#         width: 100%;
#         border-collapse: collapse;
#         border: none !important;
#     }

#     .tabela-clean thead,
#     .tabela-clean tbody,
#     .tabela-clean tr,
#     .tabela-clean th,
#     .tabela-clean td {
#         border: none !important;
#     }

#     .tabela-clean thead th {
#         text-align: left;
#         font-weight: 600;
#         padding: 8px 12px;
#         border-bottom: 1px solid #e6e6e6 !important;
#     }

#     .tabela-clean tbody td {
#         padding: 10px 12px;
#     }

#     .tabela-clean table th:first-child,
#     .tabela-clean table td:first-child {
#         padding-left: 0;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     return st.markdown(f'<div class="tabela-clean">{html}</div>', unsafe_allow_html=True)

def personal_table(df):

    html = df.to_html(index=False, border=0)

    st.markdown("""
    <style>
    .tabela-clean table {
        width: 100%;
        border-collapse: collapse;
        border: none !important;
    }

    .tabela-clean thead,
    .tabela-clean tbody,
    .tabela-clean tr,
    .tabela-clean th,
    .tabela-clean td {
        border: none !important;
    }

    .tabela-clean thead th {
        text-align: center;
        font-weight: 600;
        padding: 8px 12px;
        border-bottom: 5px solid #e6e6e6 !important;
    }

    .tabela-clean tbody td {
        padding: 10px 12px;
        text-align: center;
        border-bottom: 1px solid #e6e6e6 !important;
    }

    .tabela-clean table th:first-child,
    .tabela-clean table td:first-child {
        padding-left: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    return st.markdown(f'<div class="tabela-clean">{html}</div>', unsafe_allow_html=True)