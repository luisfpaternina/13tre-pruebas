��          �   %   �      p  >   q  '   �  g  �    @  &   R     y     �  %   �     �     �     	  %   !	     G	     a	     x	     �	     �	     �	     �	     �	  *   �	  3   
     I
     P
     _
     s
     x
    }
  >   �  (   �  ~    �  �  &   {     �     �  (   �               0  %   M     s     �     �     �     �     �     �       *     5   D  
   z     �     �     �     �         	                                                       
                                                           ${object.company_id.name} Order (Ref ${object.name or 'n/a' }) ('Purchase Order - %s' % (object.name)) <div style="margin: 0px; padding: 0px;">
                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                        Receive a cordial greeting, please require approval 
                        of budget increase to make the purchase request. <strong>${object.name}</strong>
                    </p>
                </div>
             <div style="margin: 0px; padding: 0px;">
    <p style="margin: 0px; padding: 0px; font-size: 13px;">
        Dears
        <br/>
        <strong> ${object.partner_id.name}</strong>
        <br/>
        % if object.partner_id.parent_id:
            <strong>(${object.partner_id.parent_id.name})</strong>
        % endif
        Good day,
        <br/>
        <br/>
        Attached purchase order No. <strong>${object.name}</strong>
        % if object.partner_ref:
            with reference: ${object.partner_ref}
        % endif
        , please keep in mind that <strong>${object.company_id.name}</strong>
        issue purchase order for the services provided or the goods purchased, 
        this document will be sent to your email directly by the financial area,
         it is <strong>NOT</strong> allowed to send purchase orders from 
         other mail and/or internal user of the company.
        <br/>
        If you have any questions, please do not hesitate to contact us.
        <br/>
        Best regards,
    </p>
</div> <strong class="mr16">Subtotal</strong> <strong>Cantidad</strong> <strong>Descripción</strong> <strong>Fecha confirmación:</strong> <strong>Fecha:</strong> <strong>IVA</strong> <strong>Referencia:</strong> <strong>Repr. del Proveedor:</strong> <strong>Subtotal</strong> <strong>Total</strong> <strong>Valor Unitario</strong> Bits - Purchase Order Email: Logo Orden de Compra (Cancelada) # Order de Compra # PO_${(object.name or '').replace('/','_')} Page: <span class="page"/> / <span class="topage"/> Phone: Purchase Order Send Purchase Order Tel: Web: Project-Id-Version: Odoo Server 13.0+e
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2020-07-07 15:24-0500
Last-Translator: 
Language-Team: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: 
Language: es_CO
X-Generator: Poedit 2.3.1
 ${object.company_id.name} Orden (Ref ${object.name or 'n/a' }) ('Orden de compra - %s' % (object.name)) <div style="margin: 0px; padding: 0px;">
                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                        Reciba un cordial saludo, por favor se requiere aprobación 
                        de aumento de presupuesto para realizar la solicitud de compra. <strong>${object.name}</strong>
                    </p>
                </div>
             <div style="margin: 0px; padding: 0px;">
    <p style="margin: 0px; padding: 0px; font-size: 13px;">
        Señores
        <br/>
        <strong> ${object.partner_id.name}</strong>
        <br/>
        % if object.partner_id.parent_id:
            <strong>(${object.partner_id.parent_id.name})</strong>
        % endif
        Buen día,
        <br/>
        <br/>
        Adjunto orden de compra No. <strong>${object.name}</strong>
        % if object.partner_ref:
            with reference: ${object.partner_ref}
        % endif
        , favor tener presente que <strong>${object.company_id.name}</strong> emite orden de compra por los servicios prestados o las mercancías adquiridas, este documento será remitido a su correo directamente por el área financiera, <strong>NOT</strong> está permitido remitir órdenes de compra desde otro correo y/o usuario interno de la compañía.
        <br/>
        Si tiene alguna pregunta, no dude en contactarnos.
        <br/>
        Atentamente,
    </p>
</div> <strong class="mr16">Subtotal</strong> <strong>Cantidad</strong> <strong>Descripción</strong> <strong>Confirmación de Fecha:</strong> <strong>Fecha:</strong> <strong>IVA</strong> <strong>Referencia:</strong> <strong>Repr. del Proveedor:</strong> <strong>Subtotal</strong> <strong> Total </strong> <strong>Valor Unitario</strong> Bits - Orden de compra Email: Logo Orden de Compra (Cancelada) # Orden de Compra # OC_${(object.name or '').replace('/','_')} Pagina: <span class="page"/> / <span class="topage"/> Teléfono: Orden de Compra Enviar orden de compra Tel: Web: 