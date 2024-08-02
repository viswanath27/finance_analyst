import os
import glob
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
from scipy import interpolate
# import logging

app = FastAPI()

# Serve static files like CSS and JS
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up the templates directory
templates = Jinja2Templates(directory="templates")
all_data = pd.DataFrame()

def process_data():
    global all_data
    folder_path = os.path.join(os.getcwd(), "data")
    csv_files = glob.glob(os.path.join(folder_path, '*.CSV'))
    print(f"number of files:{len(csv_files)}")
    # Create an empty list to store DataFrames
    data_frames = []

    # Read each .csv file and append to the list
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        data_frames.append(df)

    # Concatenate all DataFrames into a single DataFrame
    all_data = pd.concat(data_frames, ignore_index=True)
    
    # Display the combined DataFrame
    print("Combined DataFrame:\n", all_data)

    company_names = all_data['TckrSymb'].unique()
    print("Unique elements in column1:", company_names)

process_data()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    dropdown_options = [
        {"value": "ABB", "label": "ABB"},
        {"value": "AEGISLOG", "label": "AEGISLOG"},
        {"value": "ARE&M", "label": "ARE&M"},
        {"value": "AMBALALSA", "label": "AMBALALSA"},
        {"value": "ANDHRAPET", "label": "ANDHRAPET"},
        {"value": "ANSALAPI", "label": "ANSALAPI"},
        {"value": "UTIQUE", "label": "UTIQUE"},
        {"value": "ARUNAHTEL", "label": "ARUNAHTEL"},
        {"value": "BOMDYEING", "label": "BOMDYEING"},
        {"value": "ASIANHOTNR", "label": "ASIANHOTNR"},
        {"value": "ATUL", "label": "ATUL"}
    ]
    moving_average_options = [
        {"value": "5", "label": "5"},
        {"value": "10", "label": "10"},
        {"value": "15", "label": "15"},
        {"value": "20", "label": "20"},
        {"value": "25", "label": "25"},
        {"value": "30", "label": "30"},
        {"value": "35", "label": "35"},
        {"value": "40", "label": "40"},
    ]
    return templates.TemplateResponse("index.html", {"request": request, "dropdown_options": dropdown_options, "moving_average_options": moving_average_options})


@app.post("/submit", response_class=HTMLResponse)
async def handle_form(request: Request, dropdown: str = Form(...), moving_average_1: str = Form(...), moving_average_2: str = Form(...)):
    print(f"Submit clicked, selected_option :{dropdown}")
    ma_1 = int(moving_average_1)
    ma_2 = int(moving_average_2)
    print(f"Moving average 1:{ma_1}")
    print(f"Moving average 2:{ma_2}")
    required_rows = all_data[all_data['TckrSymb'] == dropdown]
    # Sort the dataframe by date to ensure proper line connection
    df = required_rows
    df['TradDt'] = pd.to_datetime(df['TradDt'])
    df = df.sort_values('TradDt')
    
    # Calculate the moving averages
    df[f'MovAvg{ma_1}'] = df['ClsPric'].rolling(window=ma_1).mean()
    df[f'MovAvg{ma_2}'] = df['ClsPric'].rolling(window=ma_2).mean()

    # Convert dates to numbers for interpolation
    x = (df['TradDt'] - df['TradDt'].min()).dt.total_seconds()
    y = df['ClsPric']
    
    # Create a smooth spline interpolation
    spline = interpolate.splrep(x, y, s=0.2)  # Adjust the smoothness factor (s) as needed
    
    # Create more points for a smoother curve
    x_smooth = pd.date_range(df['TradDt'].min(), df['TradDt'].max(), periods=500)
    x_smooth_num = (x_smooth - df['TradDt'].min()).total_seconds()
    y_smooth = interpolate.splev(x_smooth_num, spline)
    
    # Create a Plotly figure
    fig = go.Figure()
    
    # Add the smooth curve
    fig.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', name='Smooth Line', line=dict(shape='spline', smoothing=1.3, width=2)))
    
    # Add the original data points
    fig.add_trace(go.Scatter(x=df['TradDt'], y=df['ClsPric'], mode='markers', name='Data Points', marker=dict(size=6)))

    # Add the moving average lines
    fig.add_trace(go.Scatter(x=df['TradDt'], y=df[f'MovAvg{ma_1}'], mode='lines', name=f'{ma_1}-Point Moving Avg', line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=df['TradDt'], y=df[f'MovAvg{ma_2}'], mode='lines', name=f'{ma_2}-Point Moving Avg', line=dict(color='green', width=2)))
    
    fig.update_layout(
        title='Ticker variation for last 3 months',
        xaxis_title='Date',
        yaxis_title='Closing Price',
        template='plotly_white',
        hovermode="x unified",
        margin=dict(l=40, r=40, t=40, b=50)  # Increase margins to ensure border visibility
    )
    
    # Convert the figure to JSON
    fig_json = pio.to_json(fig)
    
    # Log the JSON response
    # logging.info(f"Figure JSON: {fig_json}")
    
    dropdown_options = [
        {"value": "ABB", "label": "ABB"},
        {"value": "AEGISLOG", "label": "AEGISLOG"},
        {"value": "ARE&M", "label": "ARE&M"},
        {"value": "AMBALALSA", "label": "AMBALALSA"},
        {"value": "ANDHRAPET", "label": "ANDHRAPET"},
        {"value": "ANSALAPI", "label": "ANSALAPI"},
        {"value": "UTIQUE", "label": "UTIQUE"},
        {"value": "ARUNAHTEL", "label": "ARUNAHTEL"},
        {"value": "BOMDYEING", "label": "BOMDYEING"},
        {"value": "ASIANHOTNR", "label": "ASIANHOTNR"},
        {"value": "ATUL", "label": "ATUL"}
    ]
    moving_average_options = [
        {"value": "5", "label": "5"},
        {"value": "10", "label": "10"},
        {"value": "15", "label": "15"},
        {"value": "20", "label": "20"},
        {"value": "25", "label": "25"},
        {"value": "30", "label": "30"},
        {"value": "35", "label": "35"},
        {"value": "40", "label": "40"},
    ]
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "dropdown_options": dropdown_options, 
        "moving_average_options": moving_average_options, 
        "fig_json": fig_json, 
        "selected_option": dropdown, 
        "selected_moving_average_1": moving_average_1, 
        "selected_moving_average_2": moving_average_2
    })

if __name__ == "__main__":
    import uvicorn
    print("App started and updated ")
    uvicorn.run(app, host="0.0.0.0",  port=8000)
