from odoo import models, fields, api

class AreaselectedForHR(models.Model):
    _inherit = 'equipment.allocation'
    
    area = fields.Selection(selection=[
        ('SE', 'Seguridad'),
        ('CH', 'Capital Humano'),
        ('ALM', 'Almacén'),
        ('CNT', 'Contabilidad'),
        ('ADM', 'Administrativo'),
        ('GPY', 'Gestión de pryectos'),
        ('GOP', 'Gestión operacional'),
    ], string='Area', required=True)
    
    doc_type = fields.Selection(selection=[
        ('M', 'Manual'),
        ('PR', 'Procedimiento'),
        ('PD', 'Proceso'),
        ('TR', 'Tramite'),
        ('IN', 'Instructivo'),
        ('G', 'Guía'),
        ('PG', 'Prgrama'),
        ('PL', 'Planes'),
        ('F', 'Formato'),
        ('ID', 'Indicador'),
        ('MR', 'Mapa de riesgo'),
        ('LI', 'Listas'),
        ('ARP', 'Análisis de riesgo preliminar'),
        ('RG', 'Reglamento'),
        ('VL', 'Vales'),
    ], string='Tipo de documento', required=True)