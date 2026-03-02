from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import qrcode
from PIL import Image
import os

class EventTicketGenerator:
    def __init__(self, ticket_width=105*mm, ticket_height=65*mm):
        # Standard ticket size (85mm x 55mm - credit card size)
        self.ticket_size = (ticket_width, ticket_height)
        self.buffer = BytesIO()
        self.can = canvas.Canvas(self.buffer, pagesize=self.ticket_size)
        self.event_data = {}
    
    def set_event_data(self, event_name, organizers, location, event_date, 
                      event_time, ticket_type, ticket_id, price, 
                      attendee_name=None, additional_info=None):
        self.event_data = {
            'event_name': event_name,
            'organizers': organizers,
            'location': location,
            'event_date': event_date,
            'event_time': event_time,
            'ticket_type': ticket_type,
            'ticket_id': ticket_id,
            'price': price,
            'attendee_name': attendee_name,
            'additional_info': additional_info
        }
    
    def add_background_image(self, image_path):
        """Add a background image that covers the entire ticket"""
        if os.path.exists(image_path):
            # Draw background image to cover entire ticket
            self.can.drawImage(image_path, 0, 0, 
                              width=self.ticket_size[0], 
                              height=self.ticket_size[1],
                              preserveAspectRatio=False, 
                              mask=[0, 255, 0, 255, 0, 255])#'auto')
    
    def generate_qr_code(self, data):
        """Generate a QR code with the ticket data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        return ImageReader(qr_buffer)
    
    def draw_ticket_content(self):
        """Draw all the ticket content on top of the background"""
        width, height = self.ticket_size
        
        # Set a semi-transparent white background for text areas for better readability
        self.can.setFillColorRGB(1, 1, 1, 0.6)  # White with 80% opacity
        self.can.rect(5*mm, 5*mm, width-10*mm, height-10*mm, fill=1, stroke=1)
        
        # Reset fill color to black for text
        self.can.setFillColorRGB(0, 0, 0, 1)
        
        # Event name
        self.can.setFont("Helvetica-Bold", 14)
        self.can.drawCentredString(width/2, height-15*mm, self.event_data['event_name'])
        
        # Organizers
        self.can.setFont("Helvetica", 10)
        self.can.drawCentredString(width/2, height-20*mm, f"Organized by: {self.event_data['organizers']}")
        
        # Draw a line separator
        self.can.line(10*mm, height-22*mm, width-10*mm, height-22*mm)
        
        # Location
        self.can.setFont("Helvetica-Bold", 9)
        self.can.drawString(10*mm, height-28*mm, f"Location: {self.event_data['location']}")

        self.can.setFont("Helvetica", 10)
        
        # Date and Time
        self.can.drawString(10*mm, height-32*mm, f"Date: {self.event_data['event_date']}")
        self.can.drawString(10*mm, height-36*mm, f"Time: {self.event_data['event_time']}")
        
        # Ticket info
        self.can.drawString(10*mm, height-40*mm, f"Ticket Type: {self.event_data['ticket_type']}")
        self.can.drawString(10*mm, height-44*mm, f"Price: ${self.event_data['price']:.2f}")
        
        # Attendee name if provided
        if self.event_data['attendee_name']:
            self.can.setFont("Helvetica-Bold", 10)
            self.can.drawString(10*mm, height-48*mm, f"Attendee: {self.event_data['attendee_name']}")
        
        # Generate and add QR code
        qr_data = f"Event: {self.event_data['event_name']}\nTicket ID: {self.event_data['ticket_id']}"
        qr_image = self.generate_qr_code(qr_data)
        
        # Position QR code on the right side
        qr_size = 25*mm
        self.can.drawImage(qr_image, width-30*mm, 10*mm, 
                          width=qr_size, height=qr_size, 
                          preserveAspectRatio=True, mask='auto')
        
        # Ticket ID below QR code
        self.can.setFont("Helvetica", 8)
        self.can.drawCentredString(width-17.5*mm, 8*mm, f"ID: {self.event_data['ticket_id']}")
        
        # Additional info if provided
        if self.event_data['additional_info']:
            self.can.setFont("Helvetica-Oblique", 7)
            self.can.drawString(10*mm, 5*mm, self.event_data['additional_info'])
    
    def generate_ticket(self, background_image_path=None):
        """Generate the ticket PDF with optional background image"""
        if background_image_path:
            self.add_background_image(background_image_path)
        
        self.draw_ticket_content()
        self.can.save()
        
        pdf_data = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_data
        
# Example usage
if __name__ == "__main__":
    # Create ticket generator with custom size (85mm x 55mm)
    ticket_gen = EventTicketGenerator()
    
    # Set event data
    ticket_gen.set_event_data(
        event_name="Tech Conference 2023",
        organizers="Digital Innovations Inc.",
        location="Convention Center, 123 Tech Ave",
        event_date="October 15, 2023",
        event_time="9:00 AM - 5:00 PM",
        ticket_type="VIP Pass",
        ticket_id="TC2023-VIP-0427",
        price=199.99,
        attendee_name="John Smith",
        additional_info="Includes lunch and conference materials"
    )
    
    # Generate the ticket with background image (optional)
    pdf = ticket_gen.generate_ticket(background_image_path='dasaintfavicon.jpg')
    with open("ticket_example.pdf", "wb") as f:
    	f.write(pdf)