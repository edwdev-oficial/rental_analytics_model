# Rental Analytcs Model
---

### Necessário
1. Parque de máquinas
2. Contratos de locações
3. Lista de preços da locadora

##### Parque de Máquinas
Pode ser obtido das faturas ou do Relatório retirado no HOL.
As faturas permitem analisar qualquer período relatívo a elas, já o relatório do HOL permite analisar o mês de retirada do mesmo.

##### Contratos de Locações
Devem ser fornecios pelo cliente através de um arquivo xlsx do período que se deseja analisar.
exemplo:
|numero_contrato|patrimonio|familia|marca|modelo|locacao|devolucao|valor|
|:---|:---:|:---:|:---:|:---:|:---:|:---:|---:|
|0090514|alf714|rompedor|Hilti|TE-2000|15/01/2025 10:48|19/01/2025 11:17|800,00|

Se a relação de contratos não tiver o número de patrimonio, a taxa de ocupação será calculada apenas sobre familia ou familia e modelo. Já com o número de patrimonio pode-se analisar inclusive um patrimonio específico.

##### Lista de Preços da Locadora
Caso a relação de contratos não tenha os valores, o mesmo pode ser cálculado com base nas informações desta lista
exemplo:
|familia|modelo|dia|semana|quinzena|mes|
|:---|:---:|:---:|:---:|:---:|---:|
|rompedor|TE-500|160|300|390|570|
