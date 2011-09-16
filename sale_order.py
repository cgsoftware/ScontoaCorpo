# -*- coding: utf-8 -*-



from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc

class sale_order(osv.osv):
   _inherit = "sale.order"
   _columns = {
               'valore_sconto': fields.float('Sconto a corpo', required=True, digits_compute=dp.get_precision('Sale Price'), readonly=False, states={'draft': [('readonly', False)]}),
               }
   def calcola_sco_corpo(self, cr, uid, ids, context): 
           
       if ids:
           for testa in self.browse(cr, uid, ids):
                
                for line in testa.order_line:
                    riga = {'sco_corpo':0.0,
                            'discount':self.pool.get('sale.order.line').Calcolo_Sconto(cr, uid, [line.id], line.string_discount, context)['value']['discount'],
                            }
                    ok = self.pool.get('sale.order.line').write(cr, uid, [line.id], riga)
                    
                ok = self.pool.get('sale.order').button_dummy(cr, uid, [testa.id], context)
                
                if testa.valore_sconto:
                    # c'è un importo nel valore dello sconto prima di procedere 
                    # lancia l'azzeramento per sicurezza
                    salva_sco = testa.valore_sconto
                    totale_merce = testa.amount_untaxed
                    totale_ordine = testa.amount_total
                    perc_sco = round(testa.valore_sconto * 100 / testa.amount_total, 3)
                    #import pdb;pdb.set_trace()
                    # ora cicla sulle righe e calcola la % di sconto per singola riga
                    if totale_merce <> 0:
                     for line in testa.order_line:
                      if line.price_subtotal <> 0: 
                        if line.string_discount:
                            sconto_str = line.string_discount + "+" + str(perc_sco)
                            discount_riga = self.pool.get('sale.order.line').Calcolo_Sconto(cr, uid, [line.id], sconto_str, context)['value']['discount']
                        else:
                            discount_riga = perc_sco
                        # discount_riga = (discount_riga + (discount_riga * perc_sco / 100)) # allo sconto di riga aggiunge lo sconto a corpo ribaltato sulle righe
                        riga = {
                                'sco_corpo':perc_sco,
                                'discount':discount_riga,
                                }                        
                        ok = self.pool.get('sale.order.line').write(cr, uid, [line.id], riga)
                     ok = self.pool.get('sale.order').button_dummy(cr, uid, [testa.id], context)
       return True

sale_order()


class sale_order_line(osv.osv):
    
 # def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        
            # res = super(sale_order_line, self)._amount_line(cr, uid, ids, field_name, arg, context)
 #       tax_obj = self.pool.get('account.tax')
 #       cur_obj = self.pool.get('res.currency')
 #       res = {}
 #       if context is None:
 #           context = {}
 #       for line in self.browse(cr, uid, ids, context=context):
 #           price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
 #           # toglie dal prezzo netto anche l'eventuale sconto a corpo
 #           # import pdb;pdb.set_trace()
 #           price = price * (1 - (line.sco_corpo or 0.0) / 100)
 #           taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
 #           cur = line.order_id.pricelist_id.currency_id
 #           res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        
 #       return res
    
    
  _inherit = 'sale.order.line'
  _columns = {
             'sco_corpo': fields.float('Sconto a Corpo (%)', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]}),
             # 'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute=dp.get_precision('Sale Price')),
             }
  

sale_order_line()
