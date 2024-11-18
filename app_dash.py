import dash
from dash import dcc
from dash import html
from quote_with_tv import from_lst_to_dct, summary_of_quotes
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State


"""
Создание приложения Dash
"""

external_stylesheets = [
        {
            "href": "https://fonts.googleapis.com/css2?"
                    "family=Lato:wght@400;700&display=swap",
            "rel": "stylesheet",
        }
    ]
"""
Создаем объект приложения
"""

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Прибыльные дни для работы с инструментом"
"""
Выводим пользователю стартовую страницу с поисковой стрококой
"""
app.layout = html.Div(children=[
        html.H1("Привествуем на нашей страничке, здесь вы найдете статистику по прибыльным дням", style={"text-align": "center"}),
        dcc.Input(id='input_start',
                  size='50',
                  placeholder='Введите название валюты, например EURUSD',
                  type='text',
                  value=""),
        html.Div(html.Button('Поиск', id='button_start', n_clicks=0, style={"margin-top": "10px"})),
        html.Div(id='output_start'),
        ]
    )



"""
Функция для создания графиков по прибыльным дням
"""

def create_layout(user_input, data):
    app.layout = html.Div(children=[
        dcc.Input(id='input',
                  size='50',
                  placeholder='Введите название валюты, например EURUSD',
                  type='text',
                  value=""),
        html.Div(html.Button('Поиск', id='button', n_clicks=0, style={"margin-top": "10px"})),
        html.Div(id='output'),
        html.H1(f"Статистика по дням, когда {user_input} наиболее волатилен и направлен на покупку",
                style={"text-align": "center"}),
        dcc.Graph(
            id="graph_buy",
            figure={
                "data": [
                    go.Bar(
                        x=data.columns,
                        y=data.iloc[0],
                        name="Покупка",
                        marker=dict(color="green"),
                        )
                    ],
                "layout": go.Layout(
                    title=go.layout.Title(text=f"Покупка в приоритете для {user_input}"),
                    xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text="Дни")),
                    yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text="Суммарное количество дней")),
                    width=700,
                    height=900
                    )
                },
            style={"margin-left": "25%"},

            ),
        html.H1(f"Статистика по дням, когда {user_input} наиболее волатилен и направлен на продажу",
                style={"text-align": "center"}),
        dcc.Graph(
            id="graph_sell",
            figure={
                "data": [
                    go.Bar(
                        x=data.columns,
                        y=data.iloc[1],
                        name="Продажа",
                        marker=dict(color="red"),
                        )

                    ],
                "layout": go.Layout(
                    title=go.layout.Title(text=f"Продажа в приоритете для {user_input}"),
                    xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text="Дни")),
                    yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text="Суммарное количество дней")),
                    width=700,
                    height=900
                    )
                },
            style={"margin-left": "25%"},
            ),
        ]
    )



"""
Функция для обновления графиков при перезагрузке странички
"""
@app.callback(
    Output("graph_buy", "figure"),
    Output("graph_sell", "figure"),
    Input("graph_buy", "figure"),
    Input("graph_sell", "figure"),
)
def update_graph(*args):
    try:
        return args
    except:
        return html.Div("Данные не найдены")


"""
Функция для обработки нажатия на кнопку при начале работы
"""

@app.callback(
    Output("output_start", "children"),
    Input("button_start", "n_clicks"),
    State("input_start", "value"),
)
def click_button(clicks, input_value):
    try:
        if clicks > 0 and len(input_value) > 0:
            summary_of_quotes(input_value)
            df = pd.DataFrame(from_lst_to_dct(), index=["Покупка", "Продажа"])
            df.to_csv("buy_and_sell.csv")
            data = pd.read_csv("buy_and_sell.csv")
            data.drop(columns=["Unnamed: 0"], inplace=True)
            create_layout(input_value, data)
            update_graph()
            return html.Div(html.Meta(httpEquiv="refresh", content="0; url=/"))

    except:
        return html.Div("Данные не найдены")


"""
Функция для обработки нажатия на кнопку после начала работы
"""


@app.callback(
    Output("output", "children"),
    Input("button", "n_clicks"),
    State("input", "value"),
)
def click_button(clicks, input_value):
    try:
        if clicks > 0 and len(input_value) > 0:
            summary_of_quotes(input_value)
            df = pd.DataFrame(from_lst_to_dct(), index=["Покупка", "Продажа"])
            df.to_csv("buy_and_sell.csv")
            data = pd.read_csv("buy_and_sell.csv")
            data.drop(columns=["Unnamed: 0"], inplace=True)
            create_layout(input_value, data)
            update_graph()
            return html.Div(html.Meta(httpEquiv="refresh", content="0; url=/"))

    except:
        return html.Div("Данные не найдены")


if __name__ == '__main__':
    app.run_server()

