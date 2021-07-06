#first comment

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import numpy_financial as npf


st.set_page_config(page_title="Simulateur hypothécaire")
st.title("Simulateur hypothécaire")

st.header("**Données hypothècaires**")
col1, col2 = st.beta_columns(2)

with col1:
    st.subheader("Prix de la propriété")
    home_value = st.number_input("Entrez la valeur de la propirété($): ", min_value=0.0, format='%f')
    
    st.subheader("Le taux d'intérêt")
    interest_rate = st.number_input("Entrez votre taux d'intérê(%): ", min_value=0.0, format='%f')

with col2:
    st.subheader("Mise de fonds")
    down_payment_percent = st.number_input("Entrez votre mise de fonds(%): ", min_value=0.0, format='%f')
    
    st.subheader("Durée d'amortissement (25 ans max)")
    payment_years = st.number_input("Entrez la durée d'amortissement: ", min_value=3, format='%d')


    down_payment = home_value* (down_payment_percent / 100)


loan_amount = home_value - down_payment
payment_months = payment_years*12
interest_rate = interest_rate / 100
periodic_interest_rate = (1+interest_rate)**(1/12) - 1
monthly_installment = -1*npf.pmt(periodic_interest_rate , payment_months, loan_amount)

st.subheader("**Mise de fonds:** $" + str(round(down_payment,2)))
st.subheader("**Prêt hypothécaire:** $" + str(round(loan_amount, 2)))
st.subheader("**Paiement mensuel:** $" + str(round(monthly_installment, 2)))


st.markdown("---")

st.header("**Amortissement du prêt hypothécaire**")
principal_remaining = np.zeros(payment_months)
interest_pay_arr = np.zeros(payment_months)
principal_pay_arr = np.zeros(payment_months)

for i in range(0, payment_months):
    
    if i == 0:
        previous_principal_remaining = loan_amount
    else:
        previous_principal_remaining = principal_remaining[i-1]
        
    interest_payment = round(previous_principal_remaining*periodic_interest_rate, 2)
    principal_payment = round(monthly_installment - interest_payment, 2)
    
    if previous_principal_remaining - principal_payment < 0:
        principal_payment = previous_principal_remaining
    
    interest_pay_arr[i] = interest_payment 
    principal_pay_arr[i] = principal_payment
    principal_remaining[i] = previous_principal_remaining - principal_payment
    

month_num = np.arange(payment_months)
month_num = month_num + 1

principal_remaining = np.around(principal_remaining, decimals=2)

fig = make_subplots(
    rows=2, cols=1,
    vertical_spacing=0.03,
    specs=[[{"type": "table"}],
           [{"type": "scatter"}]
          ]
)

fig.add_trace(
        go.Table(
            header=dict(
                    values=['Mois', 'Paiement du capital($)', "Paiement  d'intérêt($)", 'Balance du principal($)']
                ),
            cells = dict(
                    values =[month_num, principal_pay_arr, interest_pay_arr, principal_remaining]
                )
            ),
        row=1, col=1
    )

fig.add_trace(
        go.Scatter(
                x=month_num,
                y=principal_pay_arr,
                name= "Paiement du capital"
            ),
        row=2, col=1
    )

fig.append_trace(
        go.Scatter(
            x=month_num, 
            y=interest_pay_arr,
            name="Paiement d'intérêt"
        ),
        row=2, col=1
    )

fig.update_layout(title="Paiement de l'hypothèque échelonné sur plusieurs mois",
                   xaxis_title='Mois',
                   yaxis_title='Montan($)',
                   height= 800,
                   width = 1200,
                   legend= dict(
                           orientation="h",
                           yanchor='top',
                           y=0.47,
                           xanchor= 'left',
                           x= 0.01
                       )
                  )

st.plotly_chart(fig, use_container_width=True)


st.markdown("---")
st.header("**Valeur de la propriété (valeur fixe au marché)**")

cumulative_home_equity = np.cumsum(principal_pay_arr)
cumulative_interest_paid = np.cumsum(interest_pay_arr)

fig = go.Figure()
fig.add_trace(
        go.Scatter(
            x=month_num, 
            y=cumulative_home_equity,
            name="Valeur cumulative de la propriét"
        )
    )

fig.add_trace(
        go.Scatter(
            x=month_num, 
            y=cumulative_interest_paid,
            name="La valeur cumulative des intérêts payés"
        )
    )

fig.update_layout(title='La valeur cumulative de la propriété dans le temps',
                   xaxis_title='Mois',
                   yaxis_title='Montant($)',
                   height= 500,
                   width = 1200,
                   legend= dict(
                           orientation="h",
                           yanchor='top',
                           y=0.98,
                           xanchor= 'left',
                           x= 0.01
                       )
                  )

st.plotly_chart(fig, use_container_width=True)




st.markdown("---")
st.header("**Taux de croissance prévue**")

st.subheader("Croissance annuelle prévue")
forecast_growth = st.number_input("Entrez le taux de croissance prévu du prix(%): ",  format='%f')

growth_per_month = (forecast_growth / 12.0) / 100 
growth_array = np.full(payment_months, growth_per_month)
forecast_cumulative_growth = np.cumprod(1+growth_array)
forecast_home_value= home_value*forecast_cumulative_growth
cumulative_percent_owned = (down_payment_percent/100) + (cumulative_home_equity/home_value)
forecast_home_equity = cumulative_percent_owned*forecast_home_value

fig = go.Figure()
fig.add_trace(
        go.Scatter(
            x=month_num, 
            y=forecast_home_value,
            name="Valeur prévue de la propriété"
        )
    )

fig.add_trace(
        go.Scatter(
            x=month_num, 
            y=forecast_home_equity,
            name="Prévision de la valeur nette de la propriété"
        )
    )

fig.add_trace(
        go.Scatter(
            x=month_num, 
            y=principal_remaining,
            name="Valeur résiduelle du principal"
        )
    )

fig.update_layout(title='Valeur prévue Vs valeur nette de la propriété',
                   xaxis_title='Mois',
                   yaxis_title='Montant($)',
                   height= 500,
                   width = 1200,
                   legend= dict(
                           orientation="h",
                           yanchor='top',
                           y=1.14,
                           xanchor= 'left',
                           x= 0.01
                       )
                  )

st.plotly_chart(fig, use_container_width=True)
