
import frappe, os
import json
import base64, binascii
import uuid
from frappe.utils import  getdate
 
"""
{
     "datos":[
         {"fk_socio_cedula":"1801" ,"acti_caja_titular":0.0, "acti_caja_conyuge":0.0 },
        
     ]
}
"""
@frappe.whitelist(allow_guest=True)
def sync_analisis_capital(
        analisis_cap_cajas,
        usuario, 
        lista_cuenta_por_cobrar,
        lista_activos_bancos,
        lista_activos_plazo_fijo,
        lista_activos_vivienda,
        lista_activos_terreno,
        lista_activos_vehiculos,
        lista_activos_otros_activos,
        lista_activos_electrodomesticos,
        lista_activos_acciones,
        lista_activos_otros_activos_a,
        lista_activos_otros_activos_b,
        lista_activos_deudas_titular,
        lista_activos_deudas_conyuge,
        lista_activos_ifocom_titular,
        lista_activos_ifocom_conyuge
    ):
    tmp         = frappe.new_doc("syn_tmp")
    tmp.usuario = usuario
    tmp.socios  = str(analisis_cap_cajas)    
    tmp.insert( ignore_permissions=True )
    frappe.db.commit()
    asesor      = frappe.get_doc("Asesor",{"cedula":usuario} )
    for row in analisis_cap_cajas:
        #row = json.loads(xrow)
        #rr= json.dumps(xrow)
        #row = json.loads(rr )
        incedula = str(row['fk_socio_cedula'])
        
        socio = frappe.get_doc("Socio",{"soc_cedula":incedula})    
       
        
        existe = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_cap = frappe.new_doc('activos')
        else:
            ana_cap = frappe.get_doc("activos", {"socio":socio.name} )   

        ana_cap.acti_caja_titular = row['acti_caja_titular']
        ana_cap.acti_caja_conyuge = row['acti_caja_conyuge']
        #ana_cap.asesor = asesor.name
        ana_cap.socio = socio.name
        #activo.agencias = asesor.agencias 
        ana_cap.save(ignore_permissions=True )      

    
    
        activos_cliente = frappe.get_doc("activos", {"socio":socio.name} )  
        if activos_cliente :
            id_activo = activos_cliente.name
            frappe.db.delete("activos_ctas_dctos_x_cobrar"  , { "parent":id_activo }  )
            frappe.db.delete("activos_bancos"               , { "parent":id_activo }  )
            frappe.db.delete("activos_plazo_fijo"           , { "parent":id_activo }  )
            frappe.db.delete("activos_vivienda"             , { "parent":id_activo }  )
            frappe.db.delete("activos_terreno"              , { "parent":id_activo }  )
            frappe.db.delete("activos_vehiculos"            , { "parent":id_activo }  )
            frappe.db.delete("activos_otros_activos"        , { "parent":id_activo }  )
            frappe.db.delete("activos_electrodomesticos"    , { "parent":id_activo }  )
            frappe.db.delete("activos_acciones"             , { "parent":id_activo }  )
            frappe.db.delete("activos_otros_activos_a"      , { "parent":id_activo }  )
            frappe.db.delete("activos_otros_activos_b"      , { "parent":id_activo }  )
            frappe.db.delete("activos_deudas_titular"       , { "parent":id_activo }  )
            frappe.db.delete("activos_deudas_conyuge"       , { "parent":id_activo }  )
            frappe.db.delete("activos_ifocom_titular"       , { "parent":id_activo }  )
            frappe.db.delete("activos_ifocom_conyuge"       , { "parent":id_activo }  )
            
            


    for row in lista_cuenta_por_cobrar:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        existe      = frappe.db.exists("activos",{"socio":socio.name})

        if not existe :
            ana_cap = frappe.new_doc('activos')
        else:
            ana_cap = frappe.get_doc("activos", {"socio":socio.name} )  


        ana_cap.append("activos_ctas_dctos_x_cobrar",
        {   "detalle"           :row['detalle'],
            "parentesco"        :row['parentesco'],
            "nombre_apellido"   :row['nombre_apellido'],
            "fecha_prom_cobro"  :row['fecha_prom_cobro'],
            "monto"             :row['monto'] 
        })
        ana_cap.save(ignore_permissions=True)

    for row in lista_activos_bancos:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_ban = frappe.new_doc('activos')
        else:
            ana_ban = frappe.get_doc("activos", {"socio":socio.name} )  

        ana_ban.append("activos_bancos",{
            "instituciones" :row['instituciones'],
            "a_nombre_de"   :row['a_nombre_de'],
            "saldo"         :row['saldo'] 
        })
        ana_ban.save(ignore_permissions=True)   

    for row in lista_activos_plazo_fijo:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_pla_fijo = frappe.new_doc('activos')
        else:
            ana_pla_fijo = frappe.get_doc("activos", {"socio":socio.name} )  

        ana_pla_fijo.append("activos_plazo_fijo",{
            "institucion"     :row['institucion'],
            "a_nombre_de"       :row['a_nombre_de'],
            "fecha_vencimiento" :row['fecha_vencimiento'],
            "monto"             :row['monto'] 
        })
        ana_pla_fijo.save(ignore_permissions=True)   
       
    for row in lista_activos_vivienda:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_viv = frappe.new_doc('activos')
        else:
            ana_viv = frappe.get_doc("activos", {"socio":socio.name} )  

        ana_viv.append("activos_vivienda",{
            "num_pisos"                 :row['num_pisos'],
            "terminado_de_vivienda"     :row['terminado_de_vivienda'],
            "a_nombre_de"               :row['a_nombre_de'],
            "direccion"                 :row['direccion'],
            "hipotecado_a"              :row['hipotecado_a'],
            "valor_comercial"           :row['valor_comercial']
        })
        ana_viv.save(ignore_permissions=True)  

    for row in lista_activos_terreno:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_ter = frappe.new_doc('activos')
        else:
            ana_ter = frappe.get_doc("activos", {"socio":socio.name} )  

        ana_ter.append("activos_terreno",{
            "metros_de_terreno" :row['metros_de_terreno'],
            "valor_de_metro"    :row['valor_de_metro'],
            "a_nombre_de"       :row['a_nombre_de'],
            "direccion"         :row['direccion'],
            "hipotecado_a"      :row['hipotecado_a'],
            "valor_comercial"   :row['valor_comercial']
        })
        ana_ter.save(ignore_permissions=True)   

    for row in lista_activos_vehiculos:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_vehi = frappe.new_doc('activos')
        else:
            ana_vehi = frappe.get_doc("activos", {"socio":socio.name} )  

        ana_vehi.append("activos_vehiculos",{
            "anio_de_fabricacion"   :row['anio_de_fabricacion'],
            "tipo_de_vehiculo"      :row['tipo_de_vehiculo'],
            "marca"                 :row['marca'],
            "placa"                 :row['placa'],
            "a_nombre_de"           :row['a_nombre_de'],
            "prendado_a"            :row['prendado_a'],
            "valor_comercial"       :row['valor_comercial']
        })
        ana_vehi.save(ignore_permissions=True)   


        
    for row in lista_activos_otros_activos:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_otro = frappe.new_doc('activos')
        else:
            ana_otro = frappe.get_doc("activos", {"socio":socio.name} )  

        ana_otro.append("activos_otros_activos",{
            "cantidad"      :row['cantidad'],
            "descripcion"   :row['descripcion'],
            "valor_unitario":row['valor_unitario'],
            "valor_total"   :row['valor_total']
        })
        ana_otro.save(ignore_permissions=True)   
        
    
    for row in lista_activos_electrodomesticos:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            ana_otro = frappe.new_doc('activos')
        else:
            ana_otro = frappe.get_doc("activos", {"socio":socio.name} )  

        ana_otro.append("activos_electrodomesticos",{
            "detalle"   :row['detalle'],
            "marca"     :row['marca'],
            "valor"     :row['valor']
        })
        ana_otro.save(ignore_permissions=True)   


 
    for row in lista_activos_acciones:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            reg_documento =  ('activos')
        else:
            reg_documento = frappe.get_doc("activos", {"socio":socio.name} )  

        reg_documento.append("activos_acciones",{
            "nombre_entidad"        :row['nombre_entidad'],
            "fecha_deposito"        :row['fecha_deposito'],
            "nombre_inversionista"  :row['nombre_inversionista'],
            "valor"                 :row['valor']
        })
        reg_documento.save(ignore_permissions=True)   


    for row in lista_activos_otros_activos_a:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            reg_documento = frappe.new_doc('activos')
        else:
            reg_documento = frappe.get_doc("activos", {"socio":socio.name} )  

        reg_documento.append("activos_otros_activos_a",{
            "cantidad"      :row['cantidad'],
            "descripcion"   :row['descripcion'],
            "valor_unitario":row['valor_unitario'],
            "valor_total"   :row['valor_total']
        })
        reg_documento.save(ignore_permissions=True)   


 
    for row in lista_activos_otros_activos_b:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            reg_documento = frappe.new_doc('activos')
        else:
            reg_documento = frappe.get_doc("activos", {"socio":socio.name} )  

        reg_documento.append("activos_otros_activos_b",{
            "cantidad"      :row['cantidad'],
            "detalle"       :row['detalle'],
            "valor_unitario":row['valor_unitario'],
            "valor_total"   :row['valor_total']
        })
        reg_documento.save(ignore_permissions=True)        

    for row in lista_activos_deudas_titular:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            reg_documento = frappe.new_doc('activos')
        else:
            reg_documento = frappe.get_doc("activos", {"socio":socio.name} )  

        reg_documento.append("activos_deudas_titular",{
            "institucion"   :row['institucion'],
            "destino"       :row['destino'],
            "monto"         :row['monto'],
            "plazo"         :row['plazo'],
            "fecha"         :row['fecha'],
            "cuota"         :row['cuota'],
            "saldo"         :row['saldo']
        })
        reg_documento.save(ignore_permissions=True)        

    for row in lista_activos_deudas_conyuge:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            reg_documento = frappe.new_doc('activos')
        else:
            reg_documento = frappe.get_doc("activos", {"socio":socio.name} )  

        reg_documento.append("activos_deudas_conyuge",{
            "institucion"   :row['institucion'],
            "destino"       :row['destino'],
            "monto"         :row['monto'],
            "plazo"         :row['plazo'],
            "fecha"         :row['fecha'],
            "cuota"         :row['cuota'],
            "saldo"         :row['saldo']
        })
        reg_documento.save(ignore_permissions=True)        


    for row in lista_activos_ifocom_titular:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            reg_documento = frappe.new_doc('activos')
        else:
            reg_documento = frappe.get_doc("activos", {"socio":socio.name} )  

        reg_documento.append("activos_ifocom_titular",{
            "casa_comercial"    :row['casa_comercial'],
            "destino"           :row['destino'],
            "monto"             :row['monto'],
            "plazo"             :row['plazo'],
            "fecha"             :row['fecha'],
            "cuota"             :row['cuota'],
            "saldo"             :row['saldo'] 
        })
        reg_documento.save(ignore_permissions=True)        


    for row in lista_activos_ifocom_conyuge:   
        incedula    = str(row['fk_socio_cedula'])        
        socio       = frappe.get_doc("Socio",{"soc_cedula":incedula})         
        
        existe      = frappe.db.exists("activos",{"socio":socio.name})
        if not existe :
            reg_documento = frappe.new_doc('activos')
        else:
            reg_documento = frappe.get_doc("activos", {"socio":socio.name} )  

        reg_documento.append("activos_ifocom_conyuge",{
            "casa_comercial"    :row['casa_comercial'],
            "destino"           :row['destino'],
            "monto"             :row['monto'],
            "plazo"             :row['plazo'],
            "fecha"             :row['fecha'],
            "cuota"             :row['cuota'],
            "saldo"             :row['saldo'] 
        })
        reg_documento.save(ignore_permissions=True)        


    "",
    "",
    "",
    "",
    "",
    ""       

    return "OK"
 