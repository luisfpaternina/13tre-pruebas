��    $      <  5   \      0  ?   1  3   q  1   �  �  �     �     �  "     "   0     S  '   X     �  &   �     �  	   �     �     �      	     	     	  \   "	     	  `   �	  3   �	     $
     +
  
   0
     ;
     C
  
   Y
  
   d
     o
  	   x
     �
     �
     �
    �
  @   �  4   �  2   &  
  Y  !   d     �  '   �  !   �     �  1   �      #  0   D     u  
   �     �     �     �     �     �  \   �     @  b   S  5   �  
   �     �     �     	          )     2  
   B  	   M     W     f     m                                      
   	                 !                                   "                             $                                         #                 ${object.company_id.name} Invoice (Ref ${object.name or 'n/a'}) . 
                      <strong>Concept: </strong> <br/>
                          that enables from <div style="margin: 0px; padding: 0px;">
    <p style="margin: 0px; padding: 0px; font-size: 13px;">
        Dear
        % if object.partner_id.parent_id:
            ${object.partner_id.name} (${object.partner_id.parent_id.name}),
        % else:
            ${object.partner_id.name},
        % endif
        <br/><br/>
        Here is your
        % if object.name:
            invoice <strong>${object.name}</strong>
        % else:
            invoice
        %endif
        % if object.invoice_origin:
            (with reference: ${object.invoice_origin})
        % endif
        amounting in <strong>${format_amount(object.amount_total, object.currency_id)}</strong>
        from ${object.company_id.name}.
        % if object.invoice_payment_state == 'paid':
            This invoice is already paid.
        % else:
            Please remit payment at your earliest convenience.
        % endif
        <br/><br/>
        Do not hesitate to contact us if you have any questions.
    </p>
</div>
             <strong>By concept of:</strong> <strong>Currency:</strong> <strong>Related Document:</strong> <strong>Value in letters:</strong> Code Credit Note Electronic Sales Invoice No Custom Invoice Report Debit Note Electronic Sales Invoice No Description Discounts Electronic Sales Invoice No Expiration date: Free Amount Invoice Invoice date: Invoice_${(object.name or '').replace('/','_')}${object.state == 'draft' and '_draft' or ''} Journal Entries Official document of the authorization of electronic invoicing<br/>
                          No Page: <span class="page"/> / <span class="topage"/> Phone: Qty. Reference: Seller: Subtotal taxable base Unit of m. Unit price VAT rate VAT value Way to pay: charges to Project-Id-Version: Odoo Server 13.0+e
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2021-01-08 10:18-0500
Last-Translator: 
Language-Team: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: 
Language: en
X-Generator: Poedit 2.3
 ${object.company_id.name} Factura de (Ref $-object.name o 'n/a') . 
                      <strong>Concepto: </strong> <br/>
                          que habilita desde <div style="margin: 0px; padding: 0px;">
    <p style="margin: 0px; padding: 0px; font-size: 13px;">
        Estimado/a 
        % if object.partner_id.parent_id:
            ${object.partner_id.name} (${object.partner_id.parent_id.name}),
        % else:
            ${object.partner_id.name},
        % endif
        <br/><br/>
        Se remite adjunta su
        % if object.name:
            factura <strong>${object.name}</strong>
        % else:
            invoice
        %endif
        % if object.invoice_origin:
            (with reference: ${object.invoice_origin})
        % endif
        por un importe de <strong>${format_amount(object.amount_total, object.currency_id)}</strong>
        de ${object.company_id.name}.
        % if object.invoice_payment_state == 'paid':
            Esta factura ya está pagada.
        % else:
            Por favor remita el pago a su más pronta conveniencia.
        % endif
        <br/><br/>
        No dude en contactarnos si tiene alguna pregunta.
    </p>
</div>
             <strong>Por concepto de:</strong> <strong>Moneda:</strong> <strong>Documento relacionado:</strong> <strong>Valor en letras:</strong> Código Nota de crédito Factura de venta electrónica No Reporte personalizado de factura Nota de débito Factura de Venta Electrónica No Descripción Descuentos Factura electronica No Fecha de vencimiento: Monto libre Factura Fecha de la factura: Factura_${(object.name or '').replace('/','_')}${object.state == 'draft' and '_draft' or ''} Asientos contables Documento oficial de autorización de facturación electrónica <br/>
                          No Pagina: <span class="page"/> / <span class="topage"/> Teléfono: Cant. Referencia: Vendedor Subtotal base grabable Ud de m. Precio Unitario Tarifa IVA Valor IVA Forma de pago: Cargos hasta 