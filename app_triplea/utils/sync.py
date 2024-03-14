
import frappe, os
import json
import base64, binascii
import uuid
from frappe.utils import  getdate
# bench --site turismoweb execute  uio_turismo.utils.sync.getdatos
#http://newserve:8008/api/method/crediapp.utils.sync.getdatos
#https://credipasa.lexie.click/api/method/crediapp.utils.sync.getdatos
@frappe.whitelist(allow_guest=True)
def get_datos():
    sql = """ select name from tabDocType tdt  where    name in ('Socio','socios_telefonos_familiares' )  """
    data = frappe.db.sql(sql, as_dict=True)
    retorno = {}
    structure = {}
    tables = {}
    datjs = {}
    inserts = {}
    for dat in data:

        sqlcampos = """  select t.name, c.fieldname, c.fieldtype  from  tabDocField c 
            inner join tabDocType t on ( c.parent  = t.name )
            where    t.name = '{0}' 
            and fieldtype not in ('Column Break','Section Break','Read Only','Tab Break','Table') 
             and c.fieldname not in (  'naming_series')
              """.format(dat.name)
        campos = frappe.db.sql(sqlcampos, as_dict=True)
        #rows = getformat_row_js(campos, dat.name)
        #if rows:
            #inserts[dat.name] = rows

        tables[ dat.name.lower()] = getformatjs(campos)
    
    tables['usuarios'] = "([cedula] PRIMARY KEY, [password])"
    tables['solicitud_credito'] = "([name] PRIMARY KEY,  [fecha],  [monto], [plazo], [destino_credito], [intervalo], [socio],[code_sync])"
    
    tables['traking'] = "([name] PRIMARY KEY, [lon], [lat],[time],[usuario],[subido],[fecha])"
    tables['fotos'] = "([name] PRIMARY KEY, [cedula_socio], [foto] , [categoria], [detalle])"
 
 
    inserts['dat_empleado'] = get_dat_empleado()
  

    structure["tables"] = tables
    datjs["inserts"] =inserts 
    retorno = {"structure": structure, "data": datjs}
    return retorno

def get_dat_empleado():
    sql ="""  select * from `tabdat_empleado` tp WHERE  emple_correo is not null """  
    lst = frappe.db.sql(sql, as_dict=True)
    return lst

#http://newserve:8008/api/method/crediapp.utils.sync.get_dat_empleado_name?name=aaaa
#https://credipasa.lexie.click/api/method/crediapp.utils.sync.get_dat_empleado_name?name=aaaa
@frappe.whitelist(allow_guest=True)
def get_dat_empleado_name(name):
    sql = """ select DISTINCT  * from tabdat_empleado  where name ='{0}' """.format(name)
    lst = frappe.db.sql(sql, as_dict=True)
    return lst


#http://newserve:8008/api/method/crediapp.utils.sync.get_tabUser
#https://credipasa.lexie.click/api/method/crediapp.utils.sync.get_tabUser
@frappe.whitelist(allow_guest=True)
def get_tabUser():
    sql = """ select DISTINCT  full_name, email from tabUser where module_profile is not null """
    lst = frappe.db.sql(sql, as_dict=True)
    return lst


 

#http://newserve:8008/api/method/crediapp.utils.sync.getDPA
#https://credipasa.lexie.click/api/method/crediapp.utils.sync.getDPA
@frappe.whitelist(allow_guest=True)
def getDPA():
    sql =""" select *   from tabdat_empleado  """  
    lst = frappe.db.sql(sql, as_dict=True)
    return lst
    
@frappe.whitelist(allow_guest=True)
def SyncUploadTraking(listaobj,usuario):
    tmp = frappe.new_doc("syn_tmp")
    tmp.persona = usuario
    tmp.traking  = str(listaobj)     
    tmp.insert()
    frappe.db.commit()
    for row in listaobj:
        tra = frappe.new_doc("tur_tracking")
        tra.tra_gpslatitud = float(row["lat"])
        tra.tra_gpslongitud= float(row["lon"])
        tra.per_id= row["usuario"]
        tra.tra_fecha= row["fecha"]
        tra.insert()
        

 

@frappe.whitelist(allow_guest=True)
def SyncUpload_individual(lista_socios ,solicitud,usuario,cedula_socio,solicitud_name,socios_telefonos_familiares):
    tmp = frappe.new_doc("syn_tmp")
    tmp.usuario = usuario 
    tmp.socios = str(lista_socios) 
    tmp.solicitud  =str(solicitud)     
    tmp.referencias = str(socios_telefonos_familiares)    
    tmp.insert( ignore_permissions=True )
    frappe.db.commit()   

    #rr= json.dumps(lista_socios)
    row = json.loads(lista_socios )
    
    incedula = str(cedula_socio)

    existe_solicitud = frappe.db.exists("solicitud_credito",{"name":solicitud_name}) 

    existe_socio = frappe.db.exists("Socio",{"soc_cedula":incedula})    

    if( existe_socio):
        frappe.db.delete("Socio",existe_socio)

    if( existe_solicitud):
        solicitud_datos = frappe.get_doc("solicitud_credito",existe_solicitud)
        if solicitud_datos.docstatus == "1":
            return "VALIDADO"
            
        frappe.db.delete("solicitud_credito",existe_solicitud)

    socio = frappe.new_doc("Socio"  )           
    socio.soc_cedula = str(row['soc_cedula'])
    socio.soc_apellidos = row['soc_apellidos']
    socio.soc_nombres = row['soc_nombres']   
    socio.soc_pais_nac = row['soc_pais_nac']
    socio.soc_prov_nac = row['soc_prov_nac']

    socio.soc_fecha_nac =  getdate(   row['soc_fecha_nac'] )
    socio.soc_genero = row['soc_genero'] 
    socio.estadocivil = row['estadocivil']
    socio.soc_dec_jur = row['soc_dec_jur']
    socio.soc_diso_cony = row['soc_diso_cony']
    socio.soc_nivel_estudios = row['soc_nivel_estudios']
    socio.soc_profesion = row['soc_profesion']
    socio.soc_considera = row['soc_considera']
    socio.soc_discapacidad = row['soc_discapacidad']
    socio.soc_cargasf = row['soc_cargasf']
    socio.soc_hijos_estudian = row['soc_hijos_estudian'] 
    socio.soc_numerosocio = row['soc_numerosocio']
    socio.soc_telefono_conven = row['soc_telefono_conven']
    socio.soc_celular = row['soc_celular']
    socio.soc_correo = row['soc_correo']
    socio.soc_facebook = row['soc_facebook']
    socio.soc_otrasredes = row['soc_otrasredes']
    socio.soc_foto = row['soc_foto']          
    socio.zona = row['zona']
    socio.vivienda = row['vivienda'] 
    socio.duenio = row['duenio']
    socio.parentesco = row['parentesco']   
    socio.anio = row['anio']
    socio.mes = row['mes'] 
    socio.pago_mensual = row['pago_mensual']          
    socio.soc_domi_provincia = row['soc_domi_provincia']
    socio.soc_domi_canton = row['soc_domi_canton']
    socio.soc_domi_parroquia = row['soc_domi_parroquia']
    socio.barrio = row['barrio'] 
    socio.calles = row['calles']
    socio.referencia_domicilio = row['referencia_domicilio']
    socio.color_casa = row['color_casa'] 
    socio.no_casa = row['no_casa']
    socio.no_piso = row['no_piso']
    socio.coordenadas = row['coordenadas']            
    socio.soc_pais_domi_ext = row['soc_pais_domi_ext']
    socio.soc_prov_ext = row['soc_prov_ext'] 
    socio.ciudad_ext = row['ciudad_ext']
    socio.ident_ext = row['ident_ext'] 
    socio.codpostal_ext = row['codpostal_ext'] 
    socio.tipo = row['tipo']
    socio.lugar = row['lugar']
    socio.empresa = row['empresa']
    socio.actividad = row['actividad']  
    socio.cargo = row['cargo']
    socio.tiempo_anios = row['tiempo_anios']
    socio.tiempo_meses = row['tiempo_meses']
    socio.sueldo_utilidad = row['sueldo_utilidad']  
    socio.soc_empleo_provincia = row['soc_empleo_provincia']
    socio.soc_empleo_canton = row['soc_empleo_canton']
    socio.soc_empleo_parroquia = row['soc_empleo_parroquia']  
    socio.emp_barrio = row['emp_barrio']
    socio.emp_calles = row['emp_calles']
    socio.emp_refe = row['emp_refe'] 
    socio.emp_tel = row['emp_tel']   
    socio.emp_repre = row['emp_repre']  
    socio.emp_cargo = row['emp_cargo']  
    socio.emp_telcel = row['emp_telcel']  
    socio.cony_cedula = row['cony_cedula']
    socio.cony_apellidos = row['cony_apellidos']
    socio.cony_nombres = row['cony_nombres']
    socio.cony_pais_nac = row['cony_pais_nac']
    socio.cony_provincia_nac = row['cony_provincia_nac'] 
    socio.cony_fechanac =  getdate(   row['cony_fechanac'] )  
    socio.cony_nacionalidad = row['cony_nacionalidad']
    socio.cony_estudios = row['cony_estudios']
    socio.cony_profesion = row['cony_profesion']
    socio.cony_discapacidad = row['cony_discapacidad']  
    socio.cony_telcon = row['cony_telcon']
    socio.cony_celular = row['cony_celular']
    socio.cony_correo = row['cony_correo']
    socio.cony_facebook = row['cony_facebook']
    socio.cony_redes = row['cony_redes']
    socio.tipo_emp_cony = row['tipo_emp_cony']
    socio.lugar_emp_cony = row['lugar_emp_cony']
    socio.nom_emp_cony = row['nom_emp_cony']
    socio.activ_emp_cony = row['activ_emp_cony']
    socio.cargo_emp_cony = row['cargo_emp_cony']
    socio.tiemp_emp_cony = row['tiemp_emp_cony']
    socio.sueld_emp_cony = row['sueld_emp_cony']  
    socio.cony_empleo_provincia = row['cony_empleo_provincia']
    socio.cony_empleo_canton = row['cony_empleo_canton']
    socio.cony_empleo_parroquia = row['cony_empleo_parroquia']
    socio.barr_emp_cony = row['barr_emp_cony']  
    socio.call_emp_cony = row['call_emp_cony']
    socio.ref_emp_cony = row['ref_emp_cony']
    socio.telf_emp_cony = row['telf_emp_cony']  
    socio.repre_emp_cony = row['repre_emp_cony']  
    socio.carg_emp_cony = row['carg_emp_cony']  
    socio.tel_repr_emp_cony = row['tel_repr_emp_cony']  
    #coor = getformatCoodenadas(row["coordenadas"] )
    
    if row["croq_domi"] :
        array = row["coordenadas"].split(',')
        latitud = array[0]
        lontitud= array[1]
        newcoor = lontitud+","+latitud
        socio.croq_domi = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":['+ newcoor +']}}]}'  
        
    
    if row["coordenadas"] :
        array = row["coordenadas"].split(',')
        latitud = array[0]
        lontitud= array[1]
        newcoor = lontitud+","+latitud
        socio.croq_empleo = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":['+ newcoor +']}}]}'  
            
 
    for row in socios_telefonos_familiares:
        rfrow = json.loads(row)
        #rfrow = row 
        if rfrow['tipo'] == 'F':
            #name telefono parentesco direccion tipo nombres 
            socio.append("socios_telefonos_familiares",{"nombres":rfrow['nombres'],
            "parentesco":rfrow['parentesco'],
            "direccion":rfrow['direccion'],
            "telefono":rfrow['telefono'] })
        else:
            socio.append("socios_telefonos_nofamiliares",{"nombres":rfrow['nombres'],
            "parentesco":rfrow['parentesco'],
            "direccion":rfrow['direccion'],
            "telefono":rfrow['telefono'] })
            
    socio.insert(ignore_permissions=True )
    #frappe.db.commit()

 
    ase = frappe.get_doc("Asesor",{"cedula":usuario})
    
    #rr= json.dumps(solicitud)
    row = json.loads(solicitud )
   
    # [fecha],  [monto], [plazo], [destino_credito], [intervalo], [socio]
    sc = frappe.new_doc("solicitud_credito" )
    sc.fecha = row["fecha"]
    sc.asesor = ase.name
    sc.monto= row["fecha"]
    sc.plazo= row["plazo"]
    sc.monto = float(row["monto"])
    sc.destino= row["destino_credito"]
    sc.intervalo= row["intervalo"]        
    sc.id_movil =  row["name"]     
    socio = frappe.get_doc("Socio",{"soc_cedula":row["socio"]})
    
    sc.socio= socio.name
    sc.insert(ignore_permissions=True) 
    name_solcitud = sc.name
         
    return name_solcitud

@frappe.whitelist(allow_guest=True)
def SyncUpload(lista_socios ,lista_solicitudes,usuario ):
    tmp = frappe.new_doc("syn_tmp")
    tmp.usuario = usuario
    tmp.socios = str(lista_socios) 
    tmp.solicitudes  =str(lista_solicitudes)     
    tmp.insert( ignore_permissions=True )
    frappe.db.commit()
    
    for xrow in lista_socios:
        row = json.loads(xrow)
        #rr= json.dumps(xrow)
        #row = json.loads(rr )
        incedula = str(row['soc_cedula'])
        
        existe = frappe.db.exists("Socio",{"soc_cedula":incedula})        
        if not existe:
            socio = frappe.new_doc("Socio" )           
            socio.soc_cedula = str(row['soc_cedula'])
            socio.soc_apellidos = row['soc_apellidos']
            socio.soc_nombres = row['soc_nombres']   
            socio.soc_pais_nac = row['soc_pais_nac']
            socio.soc_prov_nac = row['soc_prov_nac']

            socio.soc_fecha_nac =  getdate(   row['soc_fecha_nac'] )
            socio.soc_genero = row['soc_genero'] 
            socio.estadocivil = row['estadocivil']
            socio.soc_dec_jur = row['soc_dec_jur']
            socio.soc_diso_cony = row['soc_diso_cony']
            socio.soc_nivel_estudios = row['soc_nivel_estudios']
            socio.soc_profesion = row['soc_profesion']
            socio.soc_considera = row['soc_considera']
            socio.soc_discapacidad = row['soc_discapacidad']
            socio.soc_cargasf = row['soc_cargasf']
            socio.soc_hijos_estudian = row['soc_hijos_estudian'] 
            socio.soc_numerosocio = row['soc_numerosocio']
            socio.soc_telefono_conven = row['soc_telefono_conven']
            socio.soc_celular = row['soc_celular']
            socio.soc_correo = row['soc_correo']
            socio.soc_facebook = row['soc_facebook']
            socio.soc_otrasredes = row['soc_otrasredes']
            socio.soc_foto = row['soc_foto']          
            socio.zona = row['zona']
            socio.vivienda = row['vivienda'] 
            socio.duenio = row['duenio']
            socio.parentesco = row['parentesco']   
            socio.anio = row['anio']
            socio.mes = row['mes'] 
            socio.pago_mensual = row['pago_mensual']          
            socio.soc_domi_provincia = row['soc_domi_provincia']
            socio.soc_domi_canton = row['soc_domi_canton']
            socio.soc_domi_parroquia = row['soc_domi_parroquia']
            socio.barrio = row['barrio'] 
            socio.calles = row['calles']
            socio.referencia_domicilio = row['referencia_domicilio']
            socio.color_casa = row['color_casa'] 
            socio.no_casa = row['no_casa']
            socio.no_piso = row['no_piso']
            socio.coordenadas = row['coordenadas']            
            socio.soc_pais_domi_ext = row['soc_pais_domi_ext']
            socio.soc_prov_ext = row['soc_prov_ext'] 
            socio.ciudad_ext = row['ciudad_ext']
            socio.ident_ext = row['ident_ext'] 
            socio.codpostal_ext = row['codpostal_ext'] 
            socio.tipo = row['tipo']
            socio.lugar = row['lugar']
            socio.empresa = row['empresa']
            socio.actividad = row['actividad']  
            socio.cargo = row['cargo']
            socio.tiempo_anios = row['tiempo_anios']
            socio.tiempo_meses = row['tiempo_meses']
            socio.sueldo_utilidad = row['sueldo_utilidad']  
            socio.soc_empleo_provincia = row['soc_empleo_provincia']
            socio.soc_empleo_canton = row['soc_empleo_canton']
            socio.soc_empleo_parroquia = row['soc_empleo_parroquia']  
            socio.emp_barrio = row['emp_barrio']
            socio.emp_calles = row['emp_calles']
            socio.emp_refe = row['emp_refe'] 
            socio.emp_tel = row['emp_tel']   
            socio.emp_repre = row['emp_repre']  
            socio.emp_cargo = row['emp_cargo']  
            socio.emp_telcel = row['emp_telcel']  
            socio.cony_cedula = row['cony_cedula']
            socio.cony_apellidos = row['cony_apellidos']
            socio.cony_nombres = row['cony_nombres']
            socio.cony_pais_nac = row['cony_pais_nac']
            socio.cony_provincia_nac = row['cony_provincia_nac'] 
            socio.cony_fechanac =  getdate(   row['cony_fechanac'] )  
            socio.cony_nacionalidad = row['cony_nacionalidad']
            socio.cony_estudios = row['cony_estudios']
            socio.cony_profesion = row['cony_profesion']
            socio.cony_discapacidad = row['cony_discapacidad']  
            socio.cony_telcon = row['cony_telcon']
            socio.cony_celular = row['cony_celular']
            socio.cony_correo = row['cony_correo']
            socio.cony_facebook = row['cony_facebook']
            socio.cony_redes = row['cony_redes']
            socio.tipo_emp_cony = row['tipo_emp_cony']
            socio.lugar_emp_cony = row['lugar_emp_cony']
            socio.nom_emp_cony = row['nom_emp_cony']
            socio.activ_emp_cony = row['activ_emp_cony']
            socio.cargo_emp_cony = row['cargo_emp_cony']
            socio.tiemp_emp_cony = row['tiemp_emp_cony']
            socio.sueld_emp_cony = row['sueld_emp_cony']  
            socio.cony_empleo_provincia = row['cony_empleo_provincia']
            socio.cony_empleo_canton = row['cony_empleo_canton']
            socio.cony_empleo_parroquia = row['cony_empleo_parroquia']
            socio.barr_emp_cony = row['barr_emp_cony']  
            socio.call_emp_cony = row['call_emp_cony']
            socio.ref_emp_cony = row['ref_emp_cony']
            socio.telf_emp_cony = row['telf_emp_cony']  
            socio.repre_emp_cony = row['repre_emp_cony']  
            socio.carg_emp_cony = row['carg_emp_cony']  
            socio.tel_repr_emp_cony = row['tel_repr_emp_cony']  
            #coor = getformatCoodenadas(row["coordenadas"] )

 

            if row["croq_domi"] :
                array = row["coordenadas"].split(',')
                latitud = array[0]
                lontitud= array[1]
                newcoor = lontitud+","+latitud
                socio.croq_domi = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":['+ newcoor +']}}]}'  
               
            
            if row["coordenadas"] :
                array = row["coordenadas"].split(',')
                latitud = array[0]
                lontitud= array[1]
                newcoor = lontitud+","+latitud
                socio.croq_empleo = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":['+ newcoor +']}}]}'  
                 


            socio.insert(ignore_permissions=True )
            frappe.db.commit()

 
    ase = frappe.get_doc("Asesor",{"cedula":usuario})
    name_solcitud=''
    
    for xrow in lista_solicitudes:
        #rr = json.dumps(xrow)
        #row = json.loads(rr)
        row = json.loads(xrow)
        # [fecha],  [monto], [plazo], [destino_credito], [intervalo], [socio]
        sc = frappe.new_doc("solicitud_credito" )
        sc.fecha = row["fecha"]
        sc.asesor = ase.name
        sc.monto= row["fecha"]
        sc.plazo= row["plazo"]
        sc.monto = float(row["monto"])
        sc.destino= row["destino_credito"]
        sc.intervalo= row["intervalo"]        
        sc.id_movil =  row["name"]     
        socio = frappe.get_doc("Socio",{"soc_cedula":row["socio"]})
        
        sc.socio= socio.name
        sc.insert(ignore_permissions=True) 
        name_solcitud = sc.name
         
    return name_solcitud

def getformatCoodenadas(srt_coordenadas):
    #"croq_domi":"Latitud:-1.2164427,Longitud:-78.6138518"
    if srt_coordenadas:
        """text1 = srt_coordenadas.split(',')
        text2 = text1[0].split(":")
        latitud = text2[1]
        text2 = text1[1].split(":")
        lontitud = text2[1]"""
        array = str( srt_coordenadas).split(',')
        latitud = array[0]
        lontitud= array[1]
        valor ={
             "type": "FeatureCollection",
                                        "features": [{
                                            "type": "Feature",
                                            "properties": {},
                                            "geometry": {
                                                "type": "Point",
                                                "coordinates": [
                                                float(lontitud),
                                                   float(latitud)

                                                ]
                                            }
                                        }]
                                    }
     
        return  valor 
    else:
        return None
    


@frappe.whitelist(allow_guest=True)
def SyncUploadReferencias(socios_telefonos_familiares,cedula_socio):
      
    tmp = frappe.new_doc("syn_tmp")
    tmp.usuario = "referen"
    tmp.foto = str(socios_telefonos_familiares )
    tmp.insert( ignore_permissions=True )
    frappe.db.commit()

    existe = frappe.db.exists("Socio",{"soc_cedula":str(cedula_socio)})
    if existe:
        socio = frappe.get_doc("Socio",str(cedula_socio))
        socio.socios_telefonos_familiares = []
        socio.socios_telefonos_nofamiliares = []
        socio.save()
        frappe.db.commit()


    for row in socios_telefonos_familiares:
        #rfrow = json.loads(row)
        rfrow = row 
        existe = frappe.db.exists("Socio",{"soc_cedula":rfrow['padre']})  
        if existe:
            socio = frappe.get_doc("Socio",{"soc_cedula":rfrow['padre']})
            #socio.socios_telefonos_familiares=[]
            if rfrow['tipo'] == 'F':
                #name telefono parentesco direccion tipo nombres 
                socio.append("socios_telefonos_familiares",{"nombres":rfrow['nombres'],
                "parentesco":rfrow['parentesco'],
                "direccion":rfrow['direccion'],
                "telefono":rfrow['telefono'] })
            else:
                socio.append("socios_telefonos_nofamiliares",{"nombres":rfrow['nombres'],
                "parentesco":rfrow['parentesco'],
                "direccion":rfrow['direccion'],
                "telefono":rfrow['telefono'] })
            
            socio.save( ignore_permissions=True )
            frappe.db.commit()
    return "OK"

def getCanton(codigo):
    sql = """ select DISTINCT  dpa_anio, dpa_provincia , dpa_canton  from tabsil_dpa  where dpa_canton ='{0}' """.format(codigo)
    return frappe.db.sql(sql,as_dict=True)[0]

def getFormatoCampoi(name, tipo, separador):
    campo = name
    if tipo == 'Data' or tipo == 'Attach' or tipo == 'Link' or tipo == 'Small Text':
        campo = """  {0}?: string | null{1}""".format(name,separador)
    if tipo == 'Date':
        campo = """ {0}?: Date | null {1}""".format(name,separador)    
    if tipo == 'Float':
        campo = """ {0}?: number | null {1} """.format(name,separador)    
    return campo
 

 
def getformatjs(campos):
    aux = "( [name] PRIMARY KEY,"
    for camp in campos:
        aux += " [" + camp.fieldname + "],"

    retorno = aux[:-1] + ")"
    return retorno


def getformat_row_js(campos, tabla, inserDatos):
    
    if inserDatos == True:

        aux = ""
        for camp in campos:
            aux += camp.fieldname + ","

        sql = """ select  name, {0} from {1} """.format(aux[:-1], 'tab'+tabla)

        return frappe.db.sql(sql, as_dict=True)
    else:
        return []

@frappe.whitelist(allow_guest=True)
def subirfotos(stringfoto,cedula,categoria,detalle):
    ruta = os.path.abspath(frappe.get_site_path("public", "files"))
    directorio = ruta + "/"
    idpk = str( uuid.uuid1())
    archivo = ruta+'/'+cedula+"_"+idpk+".jpeg"           
    fotosrc = stringfoto.replace("data:image/jpeg;base64,", "" )
    image = base64.b64decode(fotosrc, validate=True)   
    with open(archivo, "wb") as f:
        f.write(image)
    #https://credipasa.lexie.click/files/0987652314.jpeg
    
    existe = frappe.db.exists("Socio",{"soc_cedula":cedula})        
    if existe:
        socio = frappe.get_doc("Socio",{"soc_cedula":cedula})  
        rutafoto =  '/files/'+cedula+"_"+idpk+".jpeg" 
        socio.append("socio_imagenes",{"soci_imagen":rutafoto, "soci_descripcion":categoria})         
        
        socio.save(ignore_permissions=True )  
        frappe.db.commit()



    tmp = frappe.new_doc("syn_tmp")
    tmp.usuario = cedula
    tmp.foto = archivo  
 
    tmp.insert( ignore_permissions=True )
    frappe.db.commit()
    return archivo

#https://credipasa.lexie.click/files/0987652314.jpeg

@frappe.whitelist(allow_guest=True)
def subirfotos_lista(data,cedula_socio):
    ruta = os.path.abspath(frappe.get_site_path("public", "files"))
    directorio = ruta + "/"
    existe_socio = frappe.db.exists("Socio",{"soc_cedula":cedula_socio})   
    if( existe_socio):
        socio = frappe.get_doc("Socio", existe_socio)
        socio.socio_imagenes=[]
        socio.save(ignore_permissions=True )  
        frappe.db.commit()



    for row in data:
        cedula = row["cedula"]
        categoria  = row["categoria"]
        stringfoto   = row["stringfoto"]  
        idpk = str( uuid.uuid1())
        archivo = ruta+'/'+cedula+"_"+idpk+".jpeg"           
        fotosrc = stringfoto.replace("data:image/jpeg;base64,", "" )
        image = base64.b64decode(fotosrc, validate=True)   
        with open(archivo, "wb") as f:
            f.write(image)    
        
        existe = frappe.db.exists("Socio",{"soc_cedula":cedula})        
        if existe:
            socio = frappe.get_doc("Socio",{"soc_cedula":cedula})  
            
            rutafoto =  '/files/'+cedula+"_"+idpk+".jpeg" 
            socio.append("socio_imagenes",{"soci_imagen":rutafoto, "soci_descripcion":categoria})      
            
            socio.save(ignore_permissions=True )  
            frappe.db.commit()
   
    return "Se ha subido los archivos correctamente"


@frappe.whitelist(allow_guest=True)
def subircaptura(stringfoto1,stringfoto2,cedula):
    tmp = frappe.new_doc("syn_tmp")
    tmp.usuario = cedula + "    captura"
   
  
    #data:image/jpeg;base64,
    ruta = os.path.abspath(frappe.get_site_path("public", "files"))
    directorio = ruta + "/" 
    archivo1 = ruta+'/'+cedula+"_croquis_1.jpeg"       
    stringfoto1 = str(stringfoto1)    
    fotosrc = stringfoto1.replace("data:image/png;base64,", " " ).strip()
    
 
     

    archivo2 = ruta+'/'+cedula+"_croquis_2.jpeg"
    stringfoto2 = str(stringfoto2)
    fotosrc2 = stringfoto2.replace("data:image/png;base64,", " " ).strip()
    fotosrc2 = stringfoto2.replace("data:image/png;base64,", " " ).strip()
    fotosrc2= fotosrc2.strip()
    tmp.foto = fotosrc  
    tmp.socios = fotosrc2
    #tmp.insert( ignore_permissions=True )
    #frappe.db.commit()
    
    image1 = base64.b64decode(fotosrc, validate=False)  
    with open(archivo1, "wb") as f:
        f.write(image1)
    
    
    
    image2 = base64.b64decode(fotosrc2, validate=False)   
    with open(archivo2, "wb") as f:
        f.write(image2)        


    existe = frappe.db.exists("Socio",{"soc_cedula":cedula})        
    if existe:
        socio = frappe.get_doc("Socio",{"soc_cedula":cedula})  
        socio.croq_u1 =  '/files/'+cedula+"_croquis_1.jpeg"
        if stringfoto2:
            socio.croq_u2 =  '/files/'+cedula+"_croquis_2.jpeg"        
        socio.save(ignore_permissions=True )  
        frappe.db.commit() 

    return "ok"
