acid = {
         '000368': 'C-GORE',
         '003974': 'C-GFOP',
         'DF1221': 'C-GKAK',
         'DF15D5': 'C-GEOD',
         'F91642': 'C-FZJD',
         'FEA728': 'C-FBON',
         'FF4A68': 'C-GINY'
}

class Registration:
    def __init__(self):
        with open('aircraft.canada', 'r') as ognRegistrations:
            for detail in ognRegistrations:
                #.split(",")
                values = detail.strip().split(",")
                print(values[1], values[3])
                #print(detail[1], detail[3])



    def get(radio_id):
        return acid[radio_id]
