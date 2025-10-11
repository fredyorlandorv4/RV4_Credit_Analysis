# plotting.py - FIXED VERSION with proper error handling and dark theme
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Dark theme configuration
DARK_THEME = {
    'paper_bgcolor': 'rgba(31, 41, 55, 0.6)',
    'plot_bgcolor': 'rgba(17, 24, 39, 0.4)',
    'font': {
        'color': '#F3F4F6',
        'family': 'Inter, sans-serif'
    },
    'xaxis': {
        'gridcolor': 'rgba(55, 65, 81, 0.3)',
        'zerolinecolor': 'rgba(55, 65, 81, 0.3)',
        'color': '#9CA3AF'
    },
    'yaxis': {
        'gridcolor': 'rgba(55, 65, 81, 0.3)',
        'zerolinecolor': 'rgba(55, 65, 81, 0.3)',
        'color': '#9CA3AF'
    },
    'margin': {'l': 60, 'r': 40, 't': 80, 'b': 60}
}

def create_trends_chart(df):
    """Creates application trends over time chart"""
    try:
        df = df.copy()
        
        # Ensure datetime column exists and is valid
        if 'Application_Date' not in df.columns:
            # Create dummy dates if missing
            df['Application_Date'] = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='D')
        else:
            df['Application_Date'] = pd.to_datetime(df['Application_Date'], errors='coerce')
        
        # Remove invalid dates
        df = df.dropna(subset=['Application_Date'])
        
        if len(df) == 0:
            # Return empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for trends",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="#9CA3AF")
            )
            fig.update_layout(
                paper_bgcolor=DARK_THEME['paper_bgcolor'],
                plot_bgcolor=DARK_THEME['plot_bgcolor'],
                font=DARK_THEME['font'],
                height=400,
                title="Application Volume Over Time"
            )
            return fig
        
        # Sort and resample by month
        df = df.sort_values('Application_Date')
        df_trends = df.set_index('Application_Date').resample('M')['Status'].value_counts().unstack(fill_value=0)
        
        if df_trends.empty:
            # Create simple line chart with available data
            status_counts = df.groupby(['Application_Date', 'Status']).size().reset_index(name='count')
            fig = px.line(status_counts, x='Application_Date', y='count', color='Status',
                         title="Application Volume Over Time",
                         color_discrete_map={'Approved': '#10B981', 'Withdrawn': '#F59E0B', 
                                           'Declined': '#EF4444', 'In-Process': '#3B82F6'})
        else:
            # Create multi-line chart
            fig = go.Figure()
            colors = {'Approved': '#10B981', 'Withdrawn': '#F59E0B', 
                     'Declined': '#EF4444', 'In-Process': '#3B82F6'}
            
            for col in df_trends.columns:
                fig.add_trace(go.Scatter(
                    x=df_trends.index,
                    y=df_trends[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=colors.get(col, '#9CA3AF'), width=2),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            margin=DARK_THEME['margin'],
            height=400,
            title=dict(text="Application Volume and Status Over Time", x=0.5),
            showlegend=True,
            legend=dict(
                bgcolor='rgba(31, 41, 55, 0.8)',
                bordercolor='rgba(55, 65, 81, 0.5)',
                borderwidth=1
            ),
            hovermode='x unified',
            xaxis=dict(
                gridcolor=DARK_THEME['xaxis']['gridcolor'],
                zerolinecolor=DARK_THEME['xaxis']['zerolinecolor'],
                color=DARK_THEME['xaxis']['color']
            ),
            yaxis=dict(
                gridcolor=DARK_THEME['yaxis']['gridcolor'],
                zerolinecolor=DARK_THEME['yaxis']['zerolinecolor'],
                color=DARK_THEME['yaxis']['color']
            )
        )
        return fig
        
    except Exception as e:
        print(f"Error creating trends chart: {e}")
        # Return empty chart on error
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating chart: {str(e)[:50]}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#EF4444")
        )
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            height=400
        )
        return fig

def create_funnel_chart(df):
    """Creates an application funnel chart"""
    try:
        total_apps = len(df)
        
        if total_apps == 0:
            # Return empty funnel
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for funnel",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="#9CA3AF")
            )
            fig.update_layout(
                paper_bgcolor=DARK_THEME['paper_bgcolor'],
                plot_bgcolor=DARK_THEME['plot_bgcolor'],
                font=DARK_THEME['font'],
                height=450
            )
            return fig
        
        # Calculate funnel stages
        approved_count = len(df[df['Status'] == 'Approved']) if 'Status' in df.columns else 0
        declined_count = len(df[df['Status'] == 'Declined']) if 'Status' in df.columns else 0
        in_process_count = len(df[df['Status'] == 'In-Process']) if 'Status' in df.columns else 0
        
        stages = ['Submitted', 'In Review', 'Decisioned', 'Approved']
        values = [
            total_apps,
            int(total_apps * 0.85),  # Assume 85% go to review
            approved_count + declined_count,
            approved_count
        ]
        
        # Create funnel with gradient colors
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textposition="inside",
            textinfo="value+percent initial",
            opacity=0.9,
            marker=dict(
                color=["#5C6BC0", "#42A5F5", "#29B6F6", "#26C6DA"],
                line=dict(color="rgba(255,255,255,0.2)", width=2)
            ),
            connector=dict(line=dict(color="rgba(156, 163, 175, 0.3)", width=3))
        ))
        
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            margin=DARK_THEME['margin'],
            title=dict(text="Application Funnel Analysis", x=0.5),
            height=450,
            showlegend=False
        )
        return fig
        
    except Exception as e:
        print(f"Error creating funnel chart: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating funnel: {str(e)[:50]}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#EF4444")
        )
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            height=450
        )
        return fig

def create_correlation_heatmap(df):
    """Creates a heatmap showing correlation between numeric features"""
    try:
        # Select numeric columns that are likely to exist in the data
        numeric_cols = ['Credit_Score', 'Monthly_Income', 'DTI_Ratio', 'Age', 'Processing_Time_Days']
        available_cols = [col for col in numeric_cols if col in df.columns and df[col].notna().any()]
        
        if len(available_cols) < 2:
            # Not enough data for correlation
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient numeric data for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#9CA3AF")
            )
            fig.update_layout(
                paper_bgcolor=DARK_THEME['paper_bgcolor'],
                plot_bgcolor=DARK_THEME['plot_bgcolor'],
                font=DARK_THEME['font'],
                height=450,
                title=dict(text="Feature Correlation Heatmap", x=0.5)
            )
            return fig
        
        # Ensure we have numeric data
        df_numeric = df[available_cols].select_dtypes(include=[np.number])
        
        if df_numeric.empty or len(df_numeric) < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="No valid numeric data for correlation",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#9CA3AF")
            )
            fig.update_layout(
                paper_bgcolor=DARK_THEME['paper_bgcolor'],
                plot_bgcolor=DARK_THEME['plot_bgcolor'],
                font=DARK_THEME['font'],
                height=450,
                title=dict(text="Feature Correlation Heatmap", x=0.5)
            )
            return fig
        
        # Calculate correlation matrix
        corr_matrix = df_numeric.corr()
        
        # Handle case where correlation can't be calculated
        if corr_matrix.isna().all().all():
            fig = go.Figure()
            fig.add_annotation(
                text="Unable to calculate correlations",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#9CA3AF")
            )
            fig.update_layout(
                paper_bgcolor=DARK_THEME['paper_bgcolor'],
                plot_bgcolor=DARK_THEME['plot_bgcolor'],
                font=DARK_THEME['font'],
                height=450,
                title=dict(text="Feature Correlation Heatmap", x=0.5)
            )
            return fig
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns.tolist(),
            y=corr_matrix.columns.tolist(),
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10, "color": "white"},
            colorscale=[
                [0, '#EF4444'],      # Red for negative correlation
                [0.5, '#1F2937'],    # Dark for no correlation
                [1, '#10B981']       # Green for positive correlation
            ],
            zmid=0,  # Center the colorscale at 0
            colorbar=dict(
                title="Correlation Coefficient",
                titleside="right",
                thickness=15,
                len=0.7,
                bgcolor='rgba(31, 41, 55, 0.8)',
                bordercolor='rgba(55, 65, 81, 0.5)',
                borderwidth=1,
                tickfont=dict(color='#F3F4F6')
            ),
            hoverongaps=False,
            hovertemplate='<b>%{y} vs %{x}</b><br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        # Update layout with proper structure
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            title=dict(text="Feature Correlation Heatmap", x=0.5, font=dict(size=16)),
            height=450,
            margin=DARK_THEME['margin'],
            xaxis=dict(
                tickangle=-45,
                side='bottom',
                gridcolor=DARK_THEME['xaxis']['gridcolor'],
                color=DARK_THEME['xaxis']['color']
            ),
            yaxis=dict(
                autorange='reversed',  # This ensures the heatmap displays correctly
                gridcolor=DARK_THEME['yaxis']['gridcolor'],
                color=DARK_THEME['yaxis']['color']
            )
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating correlation heatmap: {e}")
        # Return error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)[:50]}...",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#EF4444")
        )
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            height=450,
            title=dict(text="Feature Correlation Heatmap - Error", x=0.5)
        )
        return fig

def create_box_plot(df):
    """Creates box plot for credit score distribution by status"""
    try:
        if 'Credit_Score' not in df.columns or 'Status' not in df.columns:
            # Missing required columns
            fig = go.Figure()
            fig.add_annotation(
                text="Credit Score or Status data not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#9CA3AF")
            )
            fig.update_layout(
                paper_bgcolor=DARK_THEME['paper_bgcolor'],
                plot_bgcolor=DARK_THEME['plot_bgcolor'],
                font=DARK_THEME['font'],
                height=450,
                title=dict(text="Credit Score Distribution", x=0.5)
            )
            return fig
        
        # Create box plot with custom colors
        fig = go.Figure()
        
        status_colors = {
            'Approved': '#10B981',
            'Declined': '#EF4444',
            'Withdrawn': '#F59E0B',
            'In-Process': '#3B82F6'
        }
        
        for status in df['Status'].unique():
            status_data = df[df['Status'] == status]['Credit_Score']
            
            if len(status_data) > 0:  # Only add trace if we have data
                fig.add_trace(go.Box(
                    y=status_data,
                    name=status,
                    marker_color=status_colors.get(status, '#9CA3AF'),
                    boxmean='sd',  # Show mean and standard deviation
                    marker=dict(
                        outliercolor='rgba(219, 64, 82, 0.6)',
                        line=dict(
                            outliercolor='rgba(219, 64, 82, 0.6)',
                            outlierwidth=2
                        )
                    )
                ))
        
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            title=dict(text="Credit Score Distribution by Application Status", x=0.5),
            height=450,
            margin=DARK_THEME['margin'],
            showlegend=False,
            yaxis=dict(
                title="Credit Score",
                gridcolor=DARK_THEME['yaxis']['gridcolor'],
                zerolinecolor=DARK_THEME['yaxis']['zerolinecolor'],
                color=DARK_THEME['yaxis']['color']
            ),
            xaxis=dict(
                title="Application Status",
                gridcolor=DARK_THEME['xaxis']['gridcolor'],
                zerolinecolor=DARK_THEME['xaxis']['zerolinecolor'],
                color=DARK_THEME['xaxis']['color']
            )
        )
        return fig
        
    except Exception as e:
        print(f"Error creating box plot: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating box plot: {str(e)[:50]}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#EF4444")
        )
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            height=450,
            title=dict(text="Credit Score Distribution - Error", x=0.5)
        )
        return fig

def create_sunburst_chart(df):
    """Creates sunburst chart for status breakdown by gender"""
    try:
        if 'Gender' not in df.columns or 'Status' not in df.columns:
            # Missing required columns
            fig = go.Figure()
            fig.add_annotation(
                text="Gender or Status data not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#9CA3AF")
            )
            fig.update_layout(
                paper_bgcolor=DARK_THEME['paper_bgcolor'],
                plot_bgcolor=DARK_THEME['plot_bgcolor'],
                font=DARK_THEME['font'],
                height=450
            )
            return fig
        
        # Prepare data for sunburst
        df_sunburst = df.groupby(['Gender', 'Status']).size().reset_index(name='count')
        
        # Add total as root
        total_row = pd.DataFrame({
            'Gender': ['Total'],
            'Status': [''],
            'count': [df_sunburst['count'].sum()]
        })
        
        # Create hierarchy
        df_sunburst['parents'] = df_sunburst['Gender']
        total_row['parents'] = ''
        
        gender_totals = df_sunburst.groupby('Gender')['count'].sum().reset_index()
        gender_totals['Status'] = ''
        gender_totals['parents'] = 'Total'
        
        # Combine all data
        sunburst_data = pd.concat([total_row, gender_totals, df_sunburst], ignore_index=True)
        sunburst_data['labels'] = sunburst_data.apply(
            lambda x: x['Status'] if x['Status'] else x['Gender'], axis=1
        )
        
        # Create sunburst chart
        fig = go.Figure(go.Sunburst(
            labels=sunburst_data['labels'],
            parents=sunburst_data['parents'],
            values=sunburst_data['count'],
            branchvalues="total",
            marker=dict(
                colors=['#4F46E5', '#10B981', '#EF4444', '#F59E0B', '#3B82F6'] * 10,
                line=dict(color='rgba(255,255,255,0.2)', width=2)
            ),
            textinfo="label+percent parent",
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percentParent}<extra></extra>'
        ))
        
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            margin=DARK_THEME['margin'],
            title=dict(text="Application Status Breakdown by Gender", x=0.5),
            height=450
        )
        return fig
        
    except Exception as e:
        print(f"Error creating sunburst chart: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating sunburst: {str(e)[:50]}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#EF4444")
        )
        fig.update_layout(
            paper_bgcolor=DARK_THEME['paper_bgcolor'],
            plot_bgcolor=DARK_THEME['plot_bgcolor'],
            font=DARK_THEME['font'],
            height=450
        )
        return fig