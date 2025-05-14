import gradio as gr
from datetime import datetime, timedelta
import calendar

class CalendarWidget:
    def __init__(self):
        self.current_date = datetime.now()
    
    def update_month(self, direction):
        """Update current month (1 for next, -1 for previous)"""
        year = self.current_date.year
        month = self.current_date.month
        
        if direction == 1:
            month += 1
            if month > 12:
                month = 1
                year += 1
        else:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
        
        self.current_date = self.current_date.replace(year=year, month=month)
        month_name = f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
        return month_name
    
    def handle_date_click(self, day):
        """Handle date button click"""
        if day and day.strip():
            date_str = f"{self.current_date.year}-{self.current_date.month:02d}-{int(day):02d}"
            return date_str
        return None
    
    def create_interface(self):
        """Create the calendar interface"""
        with gr.Column() as calendar_widget:
            # Month and Year Selection
            with gr.Row():
                prev_month = gr.Button("◀", size="sm")
                month_display = gr.Markdown(f"{calendar.month_name[self.current_date.month]} {self.current_date.year}")
                next_month = gr.Button("▶", size="sm")
            
            # Weekday Headers
            with gr.Row():
                for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
                    gr.Markdown(f"**{day}**")
            
            # Calendar Grid
            cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
            
            # Hidden date storage
            selected_date = gr.Textbox(visible=False)
            
            # Create date buttons
            date_buttons = []
            for week in cal:
                with gr.Row():
                    for day in week:
                        if day == 0:
                            btn = gr.Button(" ", visible=False)
                        else:
                            btn = gr.Button(str(day), size="sm")
                            # Connect each date button to the date selection handler
                            btn.click(
                                fn=self.handle_date_click,
                                inputs=[btn],
                                outputs=[selected_date]
                            )
                        date_buttons.append(btn)
            
            # Handle month navigation
            prev_month.click(
                fn=lambda: self.update_month(-1),
                outputs=[month_display]
            )
            next_month.click(
                fn=lambda: self.update_month(1),
                outputs=[month_display]
            )
            
        return calendar_widget, selected_date 