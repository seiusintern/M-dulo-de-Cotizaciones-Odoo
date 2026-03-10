from odoo import models, fields, api


class Cotizacion(models.Model):
    _name = 'cotizacion.cotizacion'
    _description = 'Cotizacion Tecnica'

    name = fields.Char(string="Nombre")

    descripcion_general = fields.Text(
        string="Descripción"
    )

    user_id = fields.Many2one('res.users', string="Realizado por")

    product_id = fields.Many2one(
        'product.product',
        string="Tipo de producto"
    )

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string="Linea de orden de venta"
    )

    descripcion = fields.Text(string="Cotizacion")

    datos_tecnicos = fields.Text(string="Datos Tecnicos")

    num_ingenieros = fields.Integer(string="Numero de Ingenieros")

    num_tecnicos = fields.Integer(string="Numero de Tecnicos")

    num_dias = fields.Integer(string="Numero de dias")

    tiempo_viaje = fields.Integer(string="Tiempo de viaje ida/vuelta")

    fuera_ciudad = fields.Boolean(string="Fuera de la ciudad")

    costo_comida = fields.Float(string="Costo comida diaria (Persona)")

    costo_movilizacion = fields.Float(string="Costo movilizacion diaria (Persona)")

    costo_viaje = fields.Float(
        string="Costo viaje (Persona)",
        help="El valor ingresado se duplicará"
    )

    costo_hotel = fields.Float(string="Costo hotel noche (Persona)")

    total_laboral_sitio = fields.Float(
        string="Total laboral sitio",
        compute="_compute_totales",
        store=True
    )

    total_laboral_viaje = fields.Float(
        string="Total laboral viaje",
        compute="_compute_totales",
        store=True
    )

    total_viaticos = fields.Float(
        string="Total viaticos",
        compute="_compute_totales",
        store=True
    )

    total_transporte = fields.Float(
        string="Total transporte",
        compute="_compute_totales",
        store=True
    )

    factor_riesgo = fields.Float(string="Factor de riesgo (%)")

    costo_hora_ing = fields.Float(
        string="Costo por hora Ingeniero",
        default=12.5
    )

    costo_hora_tec = fields.Float(
        string="Costo por hora Tecnico",
        default=10.0
    )

    reduccion_standby = fields.Float(string="Reduccion por stand by (%)")

    total = fields.Float(
        string="Total",
        compute="_compute_totales",
        store=True
    )

    @api.depends(
        'num_ingenieros',
        'num_tecnicos',
        'num_dias',
        'tiempo_viaje',
        'costo_hora_ing',
        'costo_hora_tec',
        'costo_comida',
        'costo_movilizacion',
        'costo_viaje',
        'factor_riesgo'
    )
    def _compute_totales(self):

        for rec in self:

            personas = rec.num_ingenieros + rec.num_tecnicos

            # total laboral sitio
            rec.total_laboral_sitio = (
                rec.num_ingenieros * rec.num_dias * rec.costo_hora_ing * 8
                +
                rec.num_tecnicos * rec.num_dias * rec.costo_hora_tec * 8
            )

            # total laboral viaje
            rec.total_laboral_viaje = (
                rec.num_ingenieros * rec.tiempo_viaje * rec.costo_hora_ing
                +
                rec.num_tecnicos * rec.tiempo_viaje * rec.costo_hora_tec
            )

            # total viaticos
            rec.total_viaticos = (
                personas * rec.costo_comida
                +
                personas * rec.costo_viaje
            )

            # transporte
            rec.total_transporte = (
                personas * rec.costo_movilizacion
                +
                personas * rec.costo_viaje
            )

            # total base
            if rec.tiempo_viaje != 0:

                base = (
                    rec.total_laboral_sitio
                    + rec.total_laboral_viaje
                    + rec.total_viaticos
                    + rec.total_transporte
                )

            else:

                base = rec.total_laboral_sitio

            # aplicar factor de riesgo
            rec.total = base + (base * rec.factor_riesgo / 100)

    def action_agregar_linea_venta(self):

        for rec in self:

            if not rec.sale_line_id:
                return

            descripcion = f"{rec.name}\n{rec.descripcion}\nTotal: {rec.total}"

            rec.sale_line_id.write({
                'price_unit': rec.total,
                'name': descripcion
            })

    def action_ir_orden_venta(self):

        self.ensure_one()

        if not self.sale_line_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_line_id.order_id.id,
            'target': 'current'
        }
    

    def action_concatenar_cotizaciones(self):

        grupos = {}

        for rec in self:

            if not rec.sale_line_id:
                continue

            key = rec.sale_line_id.id

            if key not in grupos:
                grupos[key] = {
                    "descripcion": "",
                    "total": 0,
                    "line": rec.sale_line_id
                }

            grupos[key]["descripcion"] += f"\n{rec.descripcion}"
            grupos[key]["total"] += rec.total

        for data in grupos.values():

            line = data["line"]

            nueva_desc = (line.name or "") + "\n" + data["descripcion"]

            line.write({
                "name": nueva_desc,
                "price_unit": line.price_unit + data["total"]
            })
