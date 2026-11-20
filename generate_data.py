"""Generate FICTIONAL price-list data for practice (Northline Motors is not a real brand).
Fixed content, no randomness: every error in the configurator export is planted on purpose
so the checks can be verified. Run: python generate_data.py"""
import csv, math

# ---------- parameters ----------
VAT = 0.24
# Illustrative registration-tax scale (NOT the Greek law in force): flat rate by net-price band x CO2 multiplier
TAX_BANDS = [(0, 20000, 0.04), (20000.01, 30000, 0.08), (30000.01, 45000, 0.16), (45000.01, 10**9, 0.24)]
CO2_MULT = [(0, 0, 0.0), (1, 50, 0.25), (51, 120, 1.0), (121, 160, 1.25), (161, 999, 1.5)]
UPLIFT = {"Petrol": 0.02, "Diesel": 0.02, "PHEV": 0.03, "EV": 0.0}   # MY2027 net-price rule by fuel
OPTION_UPLIFT = 0.03

models = [  # model, body, fuel, base power kW, base CO2
 ("NL1","Hatchback","Petrol",100,128),("NL2","Sedan","Petrol",135,142),("NL2D","Sedan","Diesel",140,121),
 ("NL3","Compact SUV","Petrol",115,139),("NL4","SUV","Diesel",170,158),("NL5","Coupe","Petrol",210,176),
 ("NLE1","Hatchback","EV",150,0),("NL6","Large SUV","PHEV",230,38)]
trims = [("BASE",1.00,0,0),("SPORT",1.12,15,6),("LUX",1.22,25,9)]
base_net = {"NL1":22500,"NL2":31900,"NL2D":33400,"NL3":28700,"NL4":44800,"NL5":52900,"NLE1":38500,"NL6":61500}

variants=[]
for m,body,fuel,kw,co2 in models:
    for t,f,dkw,dco2 in trims:
        net = round(base_net[m]*f/10)*10
        variants.append(dict(variant_code=f"{m}-{t}", model=m, body=body, fuel=fuel, trim=t,
            power_kw=kw+dkw, co2_g_km=0 if fuel=="EV" else co2+(0 if fuel=="PHEV" else dco2), net_price_my2026=net))

options = [  # code, description, category, net price, available_for ("ALL" or model list), rule
 ("OP01","Metallic paint","Exterior",820,"ALL",""),
 ("OP02","19-inch alloy wheels","Exterior",1150,"ALL",""),
 ("OP03","Panoramic glass roof","Exterior",1490,"NL2;NL2D;NL3;NL4;NL6",""),
 ("OP04","Tow hitch","Exterior",690,"NL3;NL4;NL6","EXCLUDES_FUEL=EV"),
 ("OP05","Sport seats","Interior",960,"ALL","REQUIRES_TRIM=SPORT"),
 ("OP06","Leather upholstery","Interior",1980,"ALL","EXCLUDES_TRIM=BASE"),
 ("OP07","Heated front seats","Interior",420,"ALL",""),
 ("OP08","Head-up display","Technology",1060,"NL2;NL2D;NL4;NL5;NL6;NLE1",""),
 ("OP09","Premium sound system","Technology",890,"ALL",""),
 ("OP10","Adaptive cruise control","Driver assistance",1240,"ALL",""),
 ("OP11","Parking assistant with 360 camera","Driver assistance",980,"ALL",""),
 ("OP12","Adaptive LED headlights","Exterior",1120,"ALL",""),
 ("OP13","Heat pump","Technology",950,"NLE1;NL6",""),
 ("OP14","Sport exhaust","Exterior",1350,"NL5","REQUIRES_TRIM=SPORT"),
 ("OP15","Third row seats","Interior",1680,"NL4;NL6",""),
 ("OP16","Comfort access (keyless)","Technology",560,"ALL",""),
]
discontinued_options = {"OP14"}            # dropped for MY2027
new_options = [("OP17","Wireless charging pad","Technology",310,"ALL","")]
packages = [  # code, name, contents, net price MY2027
 ("PK01","Comfort Pack","OP07;OP16;OP11",1690),
 ("PK02","Technology Pack","OP08;OP09;OP10",2790),
 ("PK03","Winter Pack","OP07;OP13",1290),
]
discontinued_variants = {"NL3-BASE"}
new_variants = [dict(variant_code="NL3-SPORTPLUS", model="NL3", body="Compact SUV", fuel="Petrol", trim="SPORT PLUS",
                     power_kw=140, co2_g_km=149, net_price_my2026=None)]
NEW_VARIANT_NET_2027 = 34990

def reg_tax(net, co2):
    rate = next(r for lo,hi,r in TAX_BANDS if lo <= net <= hi)
    mult = next(m for lo,hi,m in CO2_MULT if lo <= co2 <= hi)
    return round(net*rate*mult, 2)
def retail(net, co2):
    return int(math.ceil((net*(1+VAT) + reg_tax(net,co2))/10)*10)   # round UP to next 10 EUR

# approved MY2027 list
approved=[]
for v in variants + new_variants:
    if v["variant_code"] in discontinued_variants: continue
    n27 = NEW_VARIANT_NET_2027 if v["net_price_my2026"] is None else round(v["net_price_my2026"]*(1+UPLIFT[v["fuel"]])/10)*10
    approved.append({**v, "net_price_my2027": n27, "reg_tax": reg_tax(n27, v["co2_g_km"]), "retail_price_my2027": retail(n27, v["co2_g_km"])})
opt27 = [(c,d,cat,round(p*(1+OPTION_UPLIFT)/10)*10,av,ru) for c,d,cat,p,av,ru in options if c not in discontinued_options] + new_options

def w(path, rows, cols):
    with open(path,"w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f, fieldnames=cols); wr.writeheader(); [wr.writerow({k:r.get(k,"") for k in cols}) for r in rows]

w("variants_my2026.csv", variants, ["variant_code","model","body","fuel","trim","power_kw","co2_g_km","net_price_my2026"])
w("options_my2026.csv", [dict(option_code=c,description=d,category=cat,net_price=p,available_for=av,rule=ru) for c,d,cat,p,av,ru in options],
  ["option_code","description","category","net_price","available_for","rule"])
w("price_list_my2027_approved.csv", approved, ["variant_code","model","body","fuel","trim","power_kw","co2_g_km","net_price_my2027","reg_tax","retail_price_my2027"])
w("options_my2027_approved.csv", [dict(option_code=c,description=d,category=cat,net_price=p,available_for=av,rule=ru) for c,d,cat,p,av,ru in opt27],
  ["option_code","description","category","net_price","available_for","rule"])
w("packages_my2027.csv", [dict(package_code=c,package_name=n,contents=ct,net_price=p) for c,n,ct,p in packages], ["package_code","package_name","contents","net_price"])

# ---------- configurator / invoicing export with PLANTED errors ----------
exp=[]
for a in approved:
    r = dict(item_type="VARIANT", code=a["variant_code"], model=a["model"], trim=a["trim"], fuel=a["fuel"],
             co2_g_km=a["co2_g_km"], net_price=a["net_price_my2027"], retail_price=a["retail_price_my2027"], status="ACTIVE")
    exp.append(r)
def fix(code, **kw):
    for r in exp:
        if r["code"]==code: r.update(kw)
old = {v["variant_code"]:v["net_price_my2026"] for v in variants}
# E1 price not updated (still MY2026 net, retail recomputed from it)
fix("NL2-LUX", net_price=old["NL2-LUX"], retail_price=retail(old["NL2-LUX"],[x for x in variants if x["variant_code"]=="NL2-LUX"][0]["co2_g_km"]))
# E2 typo in net price (digits swapped)
a=[x for x in approved if x["variant_code"]=="NL4-SPORT"][0]; fix("NL4-SPORT", net_price=51810)   # approved 51180 -> digits swapped (typo)
# E3 retail calculated without VAT on part (VAT 13% instead of 24%)
a=[x for x in approved if x["variant_code"]=="NL1-SPORT"][0]; fix("NL1-SPORT", retail_price=int(math.ceil((a["net_price_my2027"]*1.13+a["reg_tax"])/10)*10))
# E4 retail not rounded to 10
a=[x for x in approved if x["variant_code"]=="NL5-BASE"][0]; fix("NL5-BASE", retail_price=a["retail_price_my2027"]-3)
# E5 missing variant (new variant never loaded)
exp=[r for r in exp if r["code"]!="NL3-SPORTPLUS"]
# E6 discontinued variant still active
v=[x for x in variants if x["variant_code"]=="NL3-BASE"][0]
exp.append(dict(item_type="VARIANT", code="NL3-BASE", model="NL3", trim="BASE", fuel="Petrol", co2_g_km=v["co2_g_km"],
                net_price=v["net_price_my2026"], retail_price=retail(v["net_price_my2026"],v["co2_g_km"]), status="ACTIVE"))
# E7 duplicate row
exp.append(dict([r for r in exp if r["code"]=="NLE1-LUX"][0]))
# E8 EV with registration tax applied (CO2 wrongly 120)
a=[x for x in approved if x["variant_code"]=="NLE1-BASE"][0]; fix("NLE1-BASE", co2_g_km=120, retail_price=retail(a["net_price_my2027"],120))

# options in export: option_code x model availability rows
for c,d,cat,p,av,ru in opt27:
    exp.append(dict(item_type="OPTION", code=c, model=av, trim="", fuel="", co2_g_km="", net_price=p, retail_price=int(math.ceil(p*(1+VAT)/10)*10), status="ACTIVE"))
# E9 discontinued option still active (MY2026 price)
exp.append(dict(item_type="OPTION", code="OP14", model="NL5", trim="", fuel="", co2_g_km="", net_price=1350, retail_price=int(math.ceil(1350*1.24/10)*10), status="ACTIVE"))
# E10 option offered where the rule forbids it (tow hitch made available on EV)
for r in exp:
    if r["code"]=="OP04": r["model"]="NL3;NL4;NL6;NLE1"
# E11 option price not updated (MY2026 price)
for r in exp:
    if r["code"]=="OP10": r["net_price"]=1240; r["retail_price"]=int(math.ceil(1240*1.24/10)*10)
for c,n,ct,p in packages:
    exp.append(dict(item_type="PACKAGE", code=c, model="", trim="", fuel="", co2_g_km="", net_price=p, retail_price=int(math.ceil(p*(1+VAT)/10)*10), status="ACTIVE"))
# E12 package more expensive than buying its options separately
for r in exp:
    if r["code"]=="PK03": r["net_price"]=1450; r["retail_price"]=int(math.ceil(1450*1.24/10)*10)
w("configurator_export_my2027.csv", exp, ["item_type","code","model","trim","fuel","co2_g_km","net_price","retail_price","status"])
print(len(variants), "MY2026 variants |", len(approved), "approved MY2027 |", len(exp), "export rows")
