#!/usr/bin/env python3
"""
Wachstumsprognose-Service für Aktienanalyse
Ermittelt die 5 Aktien mit dem wahrscheinlich größten Wachstum in den nächsten 30 Tagen
"""

import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WachstumsPredictor:
    def __init__(self, api_base_url="http://localhost:8002"):
        self.api_base_url = api_base_url
        
        # Erweiterte globale Aktien-Liste (800+ Unternehmen mit Nischenbereichen und jungen Wachstumsaktien)
        self.aktien_universe = [
            # Tech-Giganten USA
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'ADBE', 'CRM',
            
            # Aufstrebende Tech USA
            'PLTR', 'SNOW', 'CRWD', 'ZM', 'DOCN', 'NET', 'DDOG', 'MDB', 'OKTA', 'ZS',
            
            # Fintech & Krypto USA
            'PYPL', 'SQ', 'COIN', 'HOOD', 'SOFI', 'UPST', 'AFRM', 'MSTR', 'OPEN', 'LMND',
            
            # Biotechnologie USA
            'MRNA', 'BNTX', 'GILD', 'REGN', 'VRTX', 'BIIB', 'AMGN', 'ILMN', 'SGEN', 'BMRN',
            
            # Clean Energy USA
            'ENPH', 'SEDG', 'FSLR', 'PLUG', 'BE', 'ICLN', 'ARRY', 'SPWR', 'NOVA', 'RUN',
            
            # Gaming & Entertainment USA
            'RBLX', 'TTWO', 'EA', 'ATVI', 'U', 'DKNG', 'PENN', 'ROKU', 'FUBO', 'SKLZ',
            
            # E-Commerce & Retail USA
            'SHOP', 'ETSY', 'EBAY', 'BABA', 'JD', 'PDD', 'SE', 'WISH', 'REAL', 'CVNA',
            
            # Automotive & Mobility USA
            'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'F', 'GM', 'HYLN', 'RIDE', 'GOEV',
            
            # Cloud & SaaS USA
            'WORK', 'TEAM', 'ASAN', 'FROG', 'PATH', 'GTLB', 'PD', 'BILL', 'DOCU',
            
            # Kleine Tech-Nebenwerte & Wachstumsaktien USA
            'AI', 'BBAI', 'SOUN', 'SMCI', 'AVAV', 'CDNS', 'SNPS', 'KLAC', 'LRCX',
            'AMAT', 'MRVL', 'QCOM', 'INTC', 'AMD', 'MU', 'NXPI', 'ADI', 'TXN',
            
            # Emerging Markets & Spezialwerte USA
            'BEKE', 'TME', 'BILI', 'VIPS', 'WB', 'KC', 'YMM', 'TIGR', 'IQ', 'NTES',
            
            # Cybersecurity Nebenwerte USA
            'S', 'CYBR', 'FEYE', 'VRNS', 'TENB', 'PING', 'RPD', 'QLYS',
            
            # Cloud & Data Analytics Nebenwerte USA
            'ESTC', 'SPLK', 'SUMO', 'FSLY', 'CFLT', 'DBX', 'BOX', 'VEEV',
            
            # Biotech Nebenwerte USA
            'TDOC', 'VEEV', 'DXCM', 'ISRG', 'PODD', 'NVTA', 'PACB', 'TWST',
            'CRSP', 'EDIT', 'NTLA', 'BEAM', 'FATE', 'BLUE', 'SRPT', 'IONS',
            
            # Renewable Energy Nebenwerte USA
            'MAXN', 'CSIQ', 'JKS', 'DQ', 'SOL', 'VSLR', 'AMPS', 'OPTT',
            
            # E-Mobility & Battery Nebenwerte USA
            'QS', 'CHPT', 'BLNK', 'EVGO', 'SBE', 'STEM', 'NKLA', 'WKHS',
            
            # Space & Defense Nebenwerte USA
            'SPCE', 'RKLB', 'ASTR', 'PL', 'IRDM', 'MAXR', 'KTOS', 'BWXT',
            
            # Food & Consumer Nebenwerte USA
            'BYND', 'OATS', 'TTCF', 'SFM', 'VERY', 'ELSE', 'APPH', 'AQB',
            
            # Cannabis & Alternative Assets USA
            'TLRY', 'CGC', 'ACB', 'CRON', 'SNDL', 'HEXO', 'OGI', 'APHA',
            
            # Real Estate Tech USA
            'RDFN', 'EXPI', 'OPAD', 'COMP', 'RMAX', 'HOUS', 'OPFI',
            
            # Junge Wachstumsaktien USA (IPO 2020-2025)
            'ABNB', 'DASH', 'PLTR', 'SNOW', 'C3AI', 'DIDI', 'GRAB', 'UBER', 'LYFT', 'ZOOM',
            'PTON', 'LMND', 'ROOT', 'OPEN', 'WISH', 'CLOV', 'MVST', 'LCID', 'RIVN', 'BROS',
            'RBLX', 'UPST', 'AFRM', 'SOFI', 'HOOD', 'DKNG', 'FUBO', 'SKLZ', 'APPS', 'BMBL',
            
            # Micro-Cap USA Nischenbereiche
            'MVIS', 'VERB', 'DGLY', 'MARK', 'UUUU', 'SMR', 'FIZZ', 'GRWG', 'CLSK', 'RIOT',
            'MARA', 'EBON', 'SOS', 'CAN', 'BTBT', 'BBIG', 'PROG', 'ATER', 'GREE', 'SPRT',
            'DWAC', 'PHUN', 'BENE', 'MARK', 'EXPR', 'BBBY', 'GME', 'AMC', 'KOSS', 'NAKD',
            
            # Deutsche Aktien (DAX, MDAX, SDAX, TecDAX)
            'BMW', 'MBG', 'VOW3', 'ALV', 'SIE', 'BAS', 'BAYN', 'DTE', 'DB1',
            'ADS', 'VNA', 'FRE', 'IFX', 'MRK', 'RWE', 'ENR', 'CON', 'HEN3',
            'BEI', 'FME', 'HEI', 'LIN', 'MTX', 'MUV2', 'PSM', 'QIA', 'RHM',
            'SAP', 'SHL', 'SY1', 'TEG', 'TKA', 'VOS', 'WDI', 'ZAL', 'PUM', 'JEN',
            'WAC', 'SZG', 'PNE3', 'WCH', 'SLT', 'DEQ', 'LEG', 'GFT', 'NEM', 'SZU',
            'HAB', 'TTK', 'GIL', 'FRA', 'VAR1', 'SRT3', 'PFV', 'AOF', 'ECX', 'DIC',
            
            # Schweizer Aktien (SMI, SLI, SMIM)
            'NESN', 'NOVN', 'ROG', 'UHR', 'UBSG', 'ABBN', 'ZURN', 'GIVN',
            'SLHN', 'SREN', 'LONN', 'GEBN', 'CSGN', 'ALC', 'SCHP', 'CFR',
            'TEMN', 'STMN', 'CLN', 'SCMN', 'SOON', 'PGHN', 'LHN', 'CLTN',
            'BUCN', 'ADEN', 'BARN', 'HOLN', 'MBTN', 'COTN', 'DKSH', 'GALE',
            
            # Französische Aktien (CAC 40, SBF 120)
            'MC', 'LVS', 'OR', 'SAN', 'TTE', 'BNP', 'ASML', 'SAF', 'AI',
            'SU', 'KER', 'RMS', 'BN', 'ACA', 'ML', 'DG', 'CAP', 'SGO',
            'CS', 'URW', 'STM', 'ORA', 'VIE', 'ATO', 'EN', 'GLE', 'TEP',
            'ERF', 'RNO', 'PUB', 'SW', 'KN', 'WLN', 'DSY', 'ENGI', 'FR', 'ALO',
            'COV', 'EL', 'BVI', 'EUCAR', 'RCO', 'TKTT', 'ATOS', 'NEOEN', 'ABCA', 'ALTHE',
            
            # Niederländische Aktien (AEX, AMX)
            'ASML', 'HEIA', 'UNA', 'PHIA', 'INGA', 'KPN', 'ABN', 'RAND',
            'WKL', 'ADYEN', 'BESI', 'JDE', 'AALB', 'IMCD', 'ASM', 'FLOW',
            'SBMO', 'AD', 'AGN', 'AKZA', 'ALFEN', 'AMG', 'APAM', 'ARCAD',
            'BAM', 'BFIT', 'CMI', 'CTAC', 'FAGR', 'FASTNED', 'FUGRO', 'HYDRA',
            
            # Britische Aktien (FTSE 100, FTSE 250)
            'SHEL', 'AZN', 'LSEG', 'ULVR', 'BP', 'GSK', 'DGE', 'VOD',
            'RIO', 'BT', 'GLEN', 'BARC', 'LLOY', 'NWG', 'TSCO', 'REL',
            'PRU', 'BHP', 'CRH', 'FLTR', 'FERG', 'IAG', 'OCDO', 'EXPN',
            'ANTO', 'AUTO', 'BDEV', 'BLND', 'BNZL', 'BRBY', 'CCL', 'CNA',
            'CRDA', 'DCC', 'DPLM', 'FCIT', 'FRAS', 'HALMA', 'HMSO', 'IHG',
            'IMB', 'INVP', 'JD', 'KGF', 'LAND', 'LGEN', 'MNG', 'MNDI',
            
            # Italienische Aktien (FTSE MIB, FTSE Italia Mid Cap)
            'ENI', 'ISP', 'UCG', 'TIT', 'STM', 'RACE', 'A2A', 'ENEL',
            'G', 'TERNA', 'SRG', 'PIRC', 'BMED', 'CNHI', 'ATL', 'MB',
            'AMP', 'AZM', 'BAMI', 'BMED', 'CAD', 'CPR', 'DIA', 'ERG',
            'FBK', 'FCA', 'FNC', 'IG', 'IP', 'LDO', 'MARR', 'MONC',
            
            # Spanische Aktien (IBEX 35, IBEX Medium Cap)
            'SAN', 'ITX', 'IBE', 'TEF', 'BBVA', 'REP', 'ELE', 'FER',
            'ACS', 'AENA', 'COL', 'IAG', 'GRF', 'SCYR', 'RED', 'ENG',
            'ACX', 'ANA', 'CABK', 'ENC', 'FCC', 'GAM', 'IAG', 'LOG',
            'MAS', 'MEL', 'MTS', 'NHH', 'PRS', 'SAB', 'TL5', 'TRE',
            
            # Norwegische Aktien (OBX, OSEBX)
            'EQNR', 'MOWI', 'NEL', 'YAR', 'SSO', 'BAKKA', 'TGS', 'KAHOT',
            'SUBC', 'NONG', 'SOAG', 'SALM', 'OTEC', 'SDRL', 'REC', 'NAS',
            'AFG', 'AKSO', 'AKA', 'AKER', 'AMSC', 'ATEA', 'AUSS', 'AWDR',
            'B2H', 'BAKKA', 'BELCO', 'BOR', 'BOUV', 'BWG', 'CAMX', 'DNB',
            
            # Schwedische Aktien (OMX Stockholm 30, Mid Cap)
            'VOLV-B', 'ATCO-A', 'ERICB', 'SEB-A', 'SWED-A', 'SAND', 'SKF-B',
            'ALFA', 'SSAB-A', 'TEL2-B', 'ELUX-B', 'SCA-B', 'BILI-B', 'NIBE-B',
            'AAK', 'ASSA-B', 'ATOS', 'AXFO', 'BANK', 'BEIJ-B', 'BETS-B', 'BILD-B',
            'BOOL', 'BURE', 'CATE', 'CLAS-B', 'CTM', 'DUST', 'EKTA-B', 'EVO',
            
            # Dänische Aktien (OMX Copenhagen 25, Mid Cap)
            'NOVO-B', 'ORSTED', 'MAERSK-B', 'DSV', 'CARL-B', 'TRYG', 'DEMANT',
            'ROCK-B', 'PANDORA', 'CHR', 'GMAB', 'AMBU-B', 'NETC', 'FLS',
            'ALKA-B', 'AMBU-B', 'BAVA', 'BPOST', 'CHRH', 'COLO-B', 'CONF', 'CPHCAP',
            'DANSKE', 'DFDS', 'DRLCO', 'GN', 'GPIG', 'GYLD', 'H2', 'ISS',
            
            # Finnische Aktien (OMX Helsinki 25, Mid Cap)
            'NOKIA', 'UPM', 'FORTUM', 'STERV', 'KNEBV', 'NESTE', 'SAMPO',
            'KESKOB', 'WRT1V', 'CGCBV', 'ORNBV', 'RTRKS', 'TYRES', 'QTCOM',
            'AFAGR', 'ATRAV', 'BIOBV', 'CAV1V', 'CGCBV', 'CITYCON', 'CTY1S', 'DEPO',
            'ELI1V', 'ELISA', 'EVLI', 'FIA1S', 'FISHC', 'FORSS', 'HUH1V', 'KAMUX',
            
            # Österreichische Aktien (ATX, ATX Prime)
            'VER', 'OMV', 'CAI', 'POST', 'EBS', 'SBO', 'RBI', 'UQA',
            'TKA', 'LNZ', 'MMK', 'WAF', 'DOC', 'FACC', 'SEM', 'AT1',
            'ANDR', 'ATS', 'CAI', 'CWI', 'EBS', 'FACC', 'FLU', 'IIA',
            'KTM', 'LNZ', 'MAYR', 'MMK', 'OMV', 'POST', 'RBI', 'SBO',
            
            # Belgische Aktien (BEL 20, BEL Mid)
            'KBC', 'UCB', 'SOLB', 'COFB', 'COSY', 'GBLB', 'ACKB', 'PROX',
            'APAQ', 'ARGX', 'COLR', 'INGA', 'AEDIFICA', 'BEFB', 'TINC', 'WDP',
            'ACKB', 'AEDIFICA', 'AGEAS', 'APAQ', 'ARGX', 'BPOST', 'CARE', 'CFE',
            'COLR', 'EKTA', 'GBLB', 'IBA', 'INGA', 'KBC', 'MELE', 'ONTEX',
            
            # Asiatische Märkte - Japan (Nikkei 225, TOPIX)
            'TSM', 'SONY', 'TM', 'NVDA', 'NTT', 'SFT', 'HMC', 'KYO', 'MFG', 'FAST',
            '6501', '6502', '6503', '6504', '6505', '6701', '6702', '6703', '6752', '6753',
            '6758', '6861', '6954', '6971', '6976', '7201', '7202', '7203', '7267', '7269',
            '7270', '7751', '7832', '7974', '8001', '8002', '8058', '8267', '8306', '8316',
            
            # Asiatische Märkte - China (SSE 50, CSI 300)
            'BABA', 'JD', 'PDD', 'BIDU', 'NTES', 'TME', 'BILI', 'IQ', 'VIPS', 'WB',
            'NIO', 'XPEV', 'LI', 'BEKE', 'DIDI', 'EDU', 'TAL', 'YMM', 'TIGR', 'KC',
            '000001', '000002', '000858', '000858', '002415', '002594', '300015', '300059',
            '600000', '600036', '600519', '600887', '601318', '601398', '601857', '601988',
            
            # Asiatische Märkte - Südkorea (KOSPI, KOSDAQ)
            'SE', 'LPL', 'KB', 'PKX', 'HMC', 'CSGP', '005930', '000660', '035420',
            '051910', '068270', '207940', '035720', '006400', '028260', '066570',
            '003550', '096770', '000270', '017670', '034730', '018260', '032830',
            
            # Asiatische Märkte - Indien (SENSEX, NIFTY)
            'INFY', 'TCS', 'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'BHARTIARTL', 'ITC',
            'HINDUNILVR', 'KOTAKBANK', 'LT', 'ASIANPAINT', 'MARUTI', 'BAJFINANCE',
            'NTPC', 'AXISBANK', 'ULTRACEMCO', 'NESTLEIND', 'TATASTEEL', 'WIPRO',
            
            # Lateinamerika - Brasilien (BOVESPA)
            'VALE', 'ITUB', 'PETR4', 'BBDC4', 'ABEV', 'B3SA3', 'JBSS3', 'MGLU3',
            'WEGE3', 'LREN3', 'SUZB3', 'RAIL3', 'CCRO3', 'GGBR4', 'CSNA3',
            'CYRE3', 'EQTL3', 'FLRY3', 'GOLL4', 'HAPV3', 'HYPE3', 'KLBN11',
            
            # Lateinamerika - Mexiko (BMV IPC)
            'GFNORTEO', 'CEMEXCPO', 'WALMEX', 'GMEXICO', 'KIMBERA', 'FEMSA',
            'TLEVICPO', 'ALPEKA', 'BIMBOA', 'ELEKTRA', 'GAPB', 'GMEXICOB',
            
            # Afrika - Südafrika (JSE All Share)
            'NPN', 'PRX', 'SHP', 'BVT', 'AGL', 'SOL', 'MTN', 'SBK', 'FSR',
            'NED', 'REM', 'ABG', 'AMS', 'APN', 'BID', 'CFR', 'CLS', 'DSY',
            
            # Australien & Ozeanien (ASX 200)
            'BHP', 'CBA', 'CSL', 'WBC', 'ANZ', 'NAB', 'WES', 'WOW', 'TLS',
            'RIO', 'MQG', 'TCL', 'STO', 'REA', 'COL', 'ALL', 'WTC', 'JHX',
            'FMG', 'SCG', 'QBE', 'WPL', 'IAG', 'ASX', 'GMG', 'S32', 'APA',
            
            # Russland (RTS, MOEX) - selektiv
            'GAZP', 'SBER', 'LKOH', 'GMKN', 'NVTK', 'ROSN', 'SNGS', 'MGNT',
            'PLZL', 'CHMF', 'ALRS', 'VTBR', 'TATN', 'IRAO', 'RUAL', 'NLMK',
            
            # Israel (TA-125)
            'TEVA', 'CHKP', 'NICE', 'CYBR', 'WDAY', 'MNDY', 'FVRR', 'WIX',
            'GLOB', 'MRNS', 'SSYS', 'ESLT', 'RDWR', 'SLDB', 'CGNT', 'OPRA',
            
            # Emerging Tech Nischen weltweit
            'GRAB', 'GOJEK', 'TOKOPEDIA', 'BUKALAPAK', 'MERCADOLIBRE', 'SEAWORLD',
            'GLOBANT', 'DESPEGAR', 'STONECO', 'PAGSEGURO', 'ARCO', 'VTEX',
            
            # Alternative Energie & Nachhaltigkeit Global
            'VWSYF', 'ORSTED', 'NEOEN', 'EDP', 'EDPR', 'EDP', 'FALCK', 'DONG',
            'VESTAS', 'GAMESA', 'NORDEX', 'ENERCON', 'SENVION', 'REPOWER',
            
            # Micro-Cap & Penny Stocks International
            'SYME', 'HGEN', 'OBSV', 'MDGS', 'VYGR', 'AVGR', 'CGEN', 'SESN',
            'ADTX', 'NTLA', 'CRSP', 'EDIT', 'BEAM', 'VERV', 'FOLD', 'ARWR',
            
            # Spezial-Situationen Global (Turnarounds, Spin-offs)
            'NKLA', 'RIDE', 'GOEV', 'CANOO', 'MULN', 'WKHS', 'ARVL', 'PSNY',
            'CCIV', 'THCB', 'IPOE', 'IPOF', 'ACTC', 'BTWN', 'FGNA', 'GRSV'
        ]
    
    def hole_aktien_daten(self, symbol: str) -> Dict[str, Any]:
        """Hole Aktieninformationen über die API"""
        try:
            response = requests.get(f"{self.api_base_url}/api/google-suche/{symbol}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Fehler beim Abrufen von {symbol}: Status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Fehler bei API-Aufruf für {symbol}: {e}")
            return None
    
    def berechne_wachstums_score(self, aktien_data: Dict[str, Any]) -> float:
        """
        Berechnet einen Wachstums-Score basierend auf verschiedenen Faktoren
        Score von 0-100, wobei 100 das höchste Wachstumspotential bedeutet
        """
        if not aktien_data or 'daten' not in aktien_data:
            return 0.0
        
        daten = aktien_data['daten']
        score = 50.0  # Basis-Score
        
        try:
            # Faktor 1: Aktuelle Performance (Gewichtung: 25%)
            change_percent_str = str(daten.get('change_percent', '0%')).replace('%', '').replace('+', '')
            try:
                daily_change = float(change_percent_str)
                if daily_change > 5:
                    score += 15
                elif daily_change > 2:
                    score += 10
                elif daily_change > 0:
                    score += 5
                elif daily_change < -5:
                    score -= 15
                elif daily_change < -2:
                    score -= 10
            except:
                pass
            
            # Faktor 2: Marktkapitalisierung-Bewertung (Gewichtung: 20%)
            market_cap = str(daten.get('market_cap', '')).upper()
            if 'T' in market_cap:  # Trillion - sehr stabil aber weniger Wachstum
                score += 5
            elif 'B' in market_cap:  # Billion - gute Balance
                try:
                    cap_value = float(market_cap.replace('B', ''))
                    if 50 <= cap_value:  # Mega Caps - niedrigeres Wachstum
                        score += 8
                    elif 10 <= cap_value < 50:  # Large Caps - moderates Wachstum
                        score += 12
                    elif 2 <= cap_value < 10:  # Mid Caps - gutes Wachstumspotential
                        score += 18
                    elif 0.3 <= cap_value < 2:  # Small Caps - hohes Wachstumspotential
                        score += 22
                    else:  # Under 300M - Micro Caps - sehr hohes Potential
                        score += 25
                except:
                    score += 15  # Default für unbekannte B-Werte
            elif 'M' in market_cap:  # Million - Micro/Nano Caps - höchstes Potential
                try:
                    cap_value = float(market_cap.replace('M', ''))
                    if cap_value >= 100:  # 100M+ - kleine aber etablierte Firmen
                        score += 28
                    elif cap_value >= 50:   # 50-100M - sehr kleine Firmen
                        score += 30
                    else:  # Under 50M - Nano Caps - extremes Potential
                        score += 35
                except:
                    score += 25
            
            # Faktor 3: KGV-Bewertung (Gewichtung: 15%)
            pe_ratio_str = str(daten.get('pe_ratio', '')).replace(',', '.')
            try:
                pe_ratio = float(pe_ratio_str)
                if 15 <= pe_ratio <= 35:  # Optimaler Bereich
                    score += 10
                elif 10 <= pe_ratio <= 50:  # Akzeptabler Bereich
                    score += 5
                elif pe_ratio > 100:  # Überteuert oder Wachstumsaktie
                    score += 15  # Kann bei Wachstumsaktien positiv sein
            except:
                score += 3  # Neutral wenn nicht verfügbar
            
            # Faktor 4: Sektor-Bonus (Gewichtung: 20%)
            symbol = aktien_data.get('symbol', '').upper()
            
            # High-Growth Tech (AI, Cloud, Cybersecurity)
            if symbol in ['NVDA', 'AMD', 'PLTR', 'SNOW', 'NET', 'CRWD', 'MDB', 'DDOG', 'AI', 'BBAI', 'SOUN', 'SMCI']:
                score += 18
            elif symbol in ['AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN']:
                score += 12
            
            # Cybersecurity Nebenwerte (hohes Wachstum)
            elif symbol in ['S', 'CYBR', 'FEYE', 'VRNS', 'TENB', 'PING', 'RPD', 'QLYS']:
                score += 16
            
            # Cloud & SaaS Nebenwerte
            elif symbol in ['ESTC', 'SPLK', 'SUMO', 'FSLY', 'CFLT', 'DBX', 'BOX', 'PD', 'BILL', 'DOCU']:
                score += 15
            
            # Semiconductor Nebenwerte
            elif symbol in ['AVAV', 'CDNS', 'SNPS', 'KLAC', 'LRCX', 'AMAT', 'MRVL', 'QCOM', 'MU', 'NXPI', 'ADI']:
                score += 14
            
            # Clean Energy & Solar (inklusive Nebenwerte)
            elif symbol in ['ENPH', 'SEDG', 'FSLR', 'PLUG', 'BE', 'MAXN', 'CSIQ', 'JKS', 'DQ', 'SOL', 'VSLR', 'NOVA', 'RUN']:
                score += 16
            
            # E-Mobility & Battery (inklusive Nebenwerte)
            elif symbol in ['TSLA', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID', 'QS', 'CHPT', 'BLNK', 'EVGO', 'STEM', 'HYLN']:
                score += 15
            
            # Biotech & Healthcare Innovation (inklusive Nebenwerte)
            elif symbol in ['MRNA', 'BNTX', 'REGN', 'VRTX', 'CRSP', 'EDIT', 'NTLA', 'BEAM', 'TDOC', 'DXCM', 'ISRG', 'PODD']:
                score += 14
            
            # Fintech (inklusive Nebenwerte)
            elif symbol in ['SQ', 'PYPL', 'COIN', 'SOFI', 'AFRM', 'HOOD', 'UPST', 'OPEN', 'LMND']:
                score += 12
            
            # Space & Defense (hohes Risiko, hohes Potential)
            elif symbol in ['SPCE', 'RKLB', 'ASTR', 'PL', 'IRDM', 'MAXR', 'KTOS', 'BWXT']:
                score += 17
            
            # Cannabis & Alternative Assets (spekulativ)
            elif symbol in ['TLRY', 'CGC', 'ACB', 'CRON', 'SNDL', 'HEXO', 'OGI', 'APHA']:
                score += 13
            
            # Gaming & Entertainment Nebenwerte
            elif symbol in ['RBLX', 'ROKU', 'FUBO', 'SKLZ', 'U', 'DKNG']:
                score += 11
            
            # Emerging Markets & China Tech
            elif symbol in ['BEKE', 'TME', 'BILI', 'VIPS', 'WB', 'KC', 'YMM', 'TIGR', 'IQ', 'NTES']:
                score += 10
            
            # Real Estate Tech
            elif symbol in ['RDFN', 'EXPI', 'OPAD', 'COMP', 'RMAX', 'HOUS', 'OPFI']:
                score += 12
            
            # Crypto Mining & Blockchain (sehr volatil)
            elif symbol in ['RIOT', 'MARA', 'CLSK', 'EBON', 'SOS', 'CAN', 'BTBT']:
                score += 15
            
            # Food Tech & Consumer Innovation
            elif symbol in ['BYND', 'OATS', 'TTCF', 'SFM', 'VERY', 'ELSE', 'APPH', 'AQB']:
                score += 11
            
            # Micro-Cap Speculative (sehr hohes Risiko/Ertrag)
            elif symbol in ['MVIS', 'VERB', 'DGLY', 'MARK', 'UUUU', 'SMR', 'FIZZ', 'GRWG']:
                score += 20
            
            # Faktor 5: Nachrichten-Sentiment (Gewichtung: 20%)
            news = daten.get('news', [])
            if news:
                positive_keywords = ['steigt', 'wächst', 'erhöht', 'positiv', 'stark', 'Gewinn', 'Erfolg', 'Rekord', 'Allzeithoch']
                negative_keywords = ['fällt', 'sinkt', 'Verlust', 'schwach', 'Problem', 'Rückgang', 'kritisch']
                
                sentiment_score = 0
                for news_item in news:
                    title = news_item.get('title', '').lower()
                    snippet = news_item.get('snippet', '').lower()
                    text = f"{title} {snippet}"
                    
                    for keyword in positive_keywords:
                        if keyword.lower() in text:
                            sentiment_score += 2
                    
                    for keyword in negative_keywords:
                        if keyword.lower() in text:
                            sentiment_score -= 2
                
                score += min(max(sentiment_score, -10), 15)  # Begrenzt auf -10 bis +15
            
            # Begrenze Score auf 0-100
            score = max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"Fehler bei Score-Berechnung: {e}")
            score = 25.0  # Fallback-Score
        
        return round(score, 2)
    
    def analysiere_alle_aktien(self) -> List[Dict[str, Any]]:
        """Analysiert alle Aktien und berechnet Wachstums-Scores"""
        logger.info(f"Starte Analyse von {len(self.aktien_universe)} Aktien (inkl. kleine Nebenwerte)...")
        
        ergebnisse = []
        
        for i, symbol in enumerate(self.aktien_universe):
            try:
                logger.info(f"Analysiere {symbol} ({i+1}/{len(self.aktien_universe)})")
                
                # Hole Aktieninformationen
                aktien_data = self.hole_aktien_daten(symbol)
                
                if aktien_data:
                    # Berechne Wachstums-Score
                    wachstums_score = self.berechne_wachstums_score(aktien_data)
                    
                    ergebnis = {
                        'symbol': symbol,
                        'name': aktien_data['daten'].get('name', symbol),
                        'current_price': aktien_data['daten'].get('current_price', 0),
                        'change_percent': aktien_data['daten'].get('change_percent', '0%'),
                        'market_cap': aktien_data['daten'].get('market_cap', 'N/A'),
                        'pe_ratio': aktien_data['daten'].get('pe_ratio', 'N/A'),
                        'wachstums_score': wachstums_score,
                        'analyse_zeit': datetime.now().isoformat(),
                        'prognose_30_tage': self.berechne_30_tage_prognose(wachstums_score, aktien_data['daten'])
                    }
                    
                    ergebnisse.append(ergebnis)
                    logger.info(f"{symbol}: Score {wachstums_score}")
                
                # Kurze Pause um API nicht zu überlasten
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Fehler bei Analyse von {symbol}: {e}")
                continue
        
        # Sortiere nach Wachstums-Score (absteigend)
        ergebnisse.sort(key=lambda x: x['wachstums_score'], reverse=True)
        
        logger.info(f"Analyse abgeschlossen. {len(ergebnisse)} Aktien erfolgreich analysiert.")
        return ergebnisse
    
    def berechne_30_tage_prognose(self, wachstums_score: float, aktien_daten: Dict) -> Dict[str, Any]:
        """Berechnet eine 30-Tage Wachstumsprognose mit Berücksichtigung von Marktkapitalisierung"""
        try:
            current_price = float(aktien_daten.get('current_price', 0))
            market_cap = str(aktien_daten.get('market_cap', '')).upper()
            
            # Volatilitäts-Multiplikator basierend auf Marktkapitalisierung
            volatility_multiplier = 1.0
            if 'M' in market_cap:  # Micro/Nano Caps - höhere Volatilität
                volatility_multiplier = 2.0
            elif 'B' in market_cap:
                try:
                    cap_value = float(market_cap.replace('B', ''))
                    if cap_value < 1:  # Small Caps unter 1B
                        volatility_multiplier = 1.5
                    elif cap_value < 10:  # Mid Caps
                        volatility_multiplier = 1.2
                except:
                    volatility_multiplier = 1.0
            
            # Basis-Wachstumsrate basierend auf Score und Marktkapitalisierung
            if wachstums_score >= 90:  # Sehr hohe Scores (oft Nebenwerte)
                growth_rate = np.random.normal(0.20 * volatility_multiplier, 0.08)  # 12-28% für Nebenwerte
            elif wachstums_score >= 80:
                growth_rate = np.random.normal(0.15 * volatility_multiplier, 0.06)  # 9-21% 
            elif wachstums_score >= 70:
                growth_rate = np.random.normal(0.10 * volatility_multiplier, 0.04)  # 6-14%
            elif wachstums_score >= 60:
                growth_rate = np.random.normal(0.06 * volatility_multiplier, 0.03)  # 3-9%
            elif wachstums_score >= 50:
                growth_rate = np.random.normal(0.03 * volatility_multiplier, 0.02)  # 1-5%
            else:
                growth_rate = np.random.normal(0.00, 0.03)  # -3% bis +3%
            
            # Extreme Werte begrenzen (aber höhere Limits für Nebenwerte)
            max_growth = 0.80 if volatility_multiplier > 1.5 else 0.50  # Bis zu 80% für Micro Caps
            min_growth = -0.50 if volatility_multiplier > 1.5 else -0.30
            growth_rate = max(min_growth, min(max_growth, growth_rate))
            
            prognostizierter_preis = current_price * (1 + growth_rate)
            
            # Risiko-Level basierend auf Volatilität und Wachstumsrate
            if volatility_multiplier >= 2.0:  # Micro Caps
                if growth_rate > 0.25:
                    risiko_level = 'Sehr Hoch'
                elif growth_rate > 0.10:
                    risiko_level = 'Hoch'
                else:
                    risiko_level = 'Mittel'
            else:  # Größere Unternehmen
                if growth_rate > 0.20:
                    risiko_level = 'Hoch'
                elif growth_rate > 0.08:
                    risiko_level = 'Mittel'
                else:
                    risiko_level = 'Niedrig'
            
            return {
                'prognostizierter_preis': round(prognostizierter_preis, 2),
                'erwartete_rendite_prozent': round(growth_rate * 100, 2),
                'vertrauen_level': 'Hoch' if wachstums_score >= 70 else 'Mittel' if wachstums_score >= 50 else 'Niedrig',
                'risiko_level': risiko_level,
                'volatilitaets_faktor': round(volatility_multiplier, 1)
            }
        except:
            return {
                'prognostizierter_preis': 0,
                'erwartete_rendite_prozent': 0,
                'vertrauen_level': 'Niedrig',
                'risiko_level': 'Unbekannt',
                'volatilitaets_faktor': 1.0
            }
    
    def erstelle_aktien_steckbrief(self, symbol: str) -> Dict[str, str]:
        """Erstellt einen Steckbrief für eine Aktie mit Firmendaten"""
        
        # Erweiterte globale Aktien-Datenbank mit WKN/ISIN für alle Märkte
        aktien_profile = {
            # USA Tech-Giganten
            'AAPL': {'name': 'Apple Inc.', 'hauptsitz': 'Cupertino, CA, USA', 'branche': 'Consumer Electronics', 'beschreibung': 'iPhone, iPad, Mac, Services', 'wkn': '865985', 'isin': 'US0378331005'},
            'MSFT': {'name': 'Microsoft Corporation', 'hauptsitz': 'Redmond, WA, USA', 'branche': 'Cloud Computing & Software', 'beschreibung': 'Azure, Office 365, Windows', 'wkn': '870747', 'isin': 'US5949181045'},
            'GOOGL': {'name': 'Alphabet Inc.', 'hauptsitz': 'Mountain View, CA, USA', 'branche': 'Internet & Search', 'beschreibung': 'Google Search, YouTube, Android', 'wkn': 'A14Y6F', 'isin': 'US02079K3059'},
            'AMZN': {'name': 'Amazon.com Inc.', 'hauptsitz': 'Seattle, WA, USA', 'branche': 'E-Commerce & Cloud', 'beschreibung': 'Online Retail, AWS Cloud', 'wkn': '906866', 'isin': 'US0231351067'},
            'META': {'name': 'Meta Platforms Inc.', 'hauptsitz': 'Menlo Park, CA, USA', 'branche': 'Social Media', 'beschreibung': 'Facebook, Instagram, WhatsApp', 'wkn': 'A1JWVX', 'isin': 'US30303M1027'},
            'TSLA': {'name': 'Tesla Inc.', 'hauptsitz': 'Austin, TX, USA', 'branche': 'Electric Vehicles', 'beschreibung': 'Elektroautos, Batterien, Solar', 'wkn': 'A1CX3T', 'isin': 'US88160R1014'},
            'NVDA': {'name': 'NVIDIA Corporation', 'hauptsitz': 'Santa Clara, CA, USA', 'branche': 'Semiconductors & AI', 'beschreibung': 'KI-Chips, Gaming GPUs', 'wkn': '918422', 'isin': 'US67066G1040'},
            'NFLX': {'name': 'Netflix Inc.', 'hauptsitz': 'Los Gatos, CA, USA', 'branche': 'Streaming Media', 'beschreibung': 'Video Streaming Platform', 'wkn': '552484', 'isin': 'US64110L1061'},
            
            # USA Aufstrebende Tech mit WKN
            'PLTR': {'name': 'Palantir Technologies', 'hauptsitz': 'Denver, CO, USA', 'branche': 'Big Data Analytics', 'beschreibung': 'KI-Software für Regierung & Unternehmen', 'wkn': 'A2QA4J', 'isin': 'US69608A1088'},
            'SNOW': {'name': 'Snowflake Inc.', 'hauptsitz': 'Bozeman, MT, USA', 'branche': 'Cloud Data Platform', 'beschreibung': 'Cloud Data Warehouse', 'wkn': 'A2QB38', 'isin': 'US8334451098'},
            'CRWD': {'name': 'CrowdStrike Holdings', 'hauptsitz': 'Austin, TX, USA', 'branche': 'Cybersecurity', 'beschreibung': 'Cloud-native Endpoint Security', 'wkn': 'A2PK2R', 'isin': 'US22788C1053'},
            'NET': {'name': 'Cloudflare Inc.', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Web Infrastructure', 'beschreibung': 'CDN, DDoS Protection, DNS', 'wkn': 'A2PQMN', 'isin': 'US18915M1071'},
            'DDOG': {'name': 'Datadog Inc.', 'hauptsitz': 'New York, NY, USA', 'branche': 'Monitoring & Analytics', 'beschreibung': 'Cloud Monitoring Platform', 'wkn': 'A2PSDL', 'isin': 'US23804L1035'},
            'MDB': {'name': 'MongoDB Inc.', 'hauptsitz': 'New York, NY, USA', 'branche': 'Database Software', 'beschreibung': 'NoSQL Database Platform', 'wkn': 'A2DQ8J', 'isin': 'US60937P1066'},
            
            # USA Fintech & Crypto mit WKN
            'COIN': {'name': 'Coinbase Global Inc.', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Cryptocurrency Exchange', 'beschreibung': 'Krypto-Handelsplattform', 'wkn': 'A2QP7J', 'isin': 'US19260Q1076'},
            'SQ': {'name': 'Block Inc. (Square)', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Financial Technology', 'beschreibung': 'Payment Processing, Bitcoin', 'wkn': 'A143D6', 'isin': 'US8522341036'},
            'SOFI': {'name': 'SoFi Technologies', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Digital Banking', 'beschreibung': 'Online Banking & Lending', 'wkn': 'A2QFL2', 'isin': 'US83406F1021'},
            'AFRM': {'name': 'Affirm Holdings', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Buy Now Pay Later', 'beschreibung': 'Ratenzahlungsdienstleister', 'wkn': 'A2QL1G', 'isin': 'US00827B1061'},
            'HOOD': {'name': 'Robinhood Markets', 'hauptsitz': 'Menlo Park, CA, USA', 'branche': 'Brokerage', 'beschreibung': 'Commission-free Trading App', 'wkn': 'A3CVQC', 'isin': 'US7707001027'},
            
            # USA Junge Wachstumsaktien (IPO 2020-2025) mit WKN
            'ABNB': {'name': 'Airbnb Inc.', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Travel Technology', 'beschreibung': 'Home Sharing Platform', 'wkn': 'A2QG35', 'isin': 'US0090661010'},
            'DASH': {'name': 'DoorDash Inc.', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Food Delivery', 'beschreibung': 'On-Demand Food Delivery', 'wkn': 'A2QEX7', 'isin': 'US25809K1051'},
            'UBER': {'name': 'Uber Technologies', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Mobility & Delivery', 'beschreibung': 'Ride-Hailing & Food Delivery', 'wkn': 'A2P6SH', 'isin': 'US90353T1007'},
            'LYFT': {'name': 'Lyft Inc.', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'Mobility Services', 'beschreibung': 'Ride-Sharing Platform', 'wkn': 'A2PE38', 'isin': 'US55087P1049'},
            'ZOOM': {'name': 'Zoom Video Communications', 'hauptsitz': 'San Jose, CA, USA', 'branche': 'Video Communications', 'beschreibung': 'Video Conferencing Platform', 'wkn': 'A2PGJ2', 'isin': 'US98980G1022'},
            'RBLX': {'name': 'Roblox Corporation', 'hauptsitz': 'San Mateo, CA, USA', 'branche': 'Gaming Platform', 'beschreibung': 'Online Gaming & Virtual Worlds', 'wkn': 'A2PX2V', 'isin': 'US7710491033'},
            'PTON': {'name': 'Peloton Interactive', 'hauptsitz': 'New York, NY, USA', 'branche': 'Connected Fitness', 'beschreibung': 'Smart Exercise Equipment', 'wkn': 'A2PR0M', 'isin': 'US70614W1009'},
            'UPST': {'name': 'Upstart Holdings', 'hauptsitz': 'San Mateo, CA, USA', 'branche': 'AI Lending', 'beschreibung': 'AI-powered Lending Platform', 'wkn': 'A2QEA6', 'isin': 'US91680M1071'},
            'RIVN': {'name': 'Rivian Automotive', 'hauptsitz': 'Irvine, CA, USA', 'branche': 'Electric Trucks', 'beschreibung': 'Electric Pickup Trucks & Vans', 'wkn': 'A3C47B', 'isin': 'US76954A1034'},
            'LCID': {'name': 'Lucid Group Inc.', 'hauptsitz': 'Newark, CA, USA', 'branche': 'Luxury Electric Cars', 'beschreibung': 'Luxury Electric Sedans', 'wkn': 'A3CVXG', 'isin': 'US5494981039'},
            
            # USA Biotechnologie mit WKN
            'MRNA': {'name': 'Moderna Inc.', 'hauptsitz': 'Cambridge, MA, USA', 'branche': 'mRNA Therapeutics', 'beschreibung': 'mRNA-Impfstoffe & Medikamente', 'wkn': 'A2N9D9', 'isin': 'US60770K1079'},
            'BNTX': {'name': 'BioNTech SE', 'hauptsitz': 'Mainz, Deutschland', 'branche': 'Immunotherapy', 'beschreibung': 'mRNA-Krebstherapie & Impfstoffe', 'wkn': 'A2PSR2', 'isin': 'US09075V1026'},
            'CRSP': {'name': 'CRISPR Therapeutics', 'hauptsitz': 'Zug, Schweiz', 'branche': 'Gene Editing', 'beschreibung': 'CRISPR Gentherapie', 'wkn': 'A2AT0Z', 'isin': 'CH0334081692'},
            'EDIT': {'name': 'Editas Medicine', 'hauptsitz': 'Cambridge, MA, USA', 'branche': 'Gene Editing', 'beschreibung': 'CRISPR Gene Editing', 'wkn': 'A2JQDC', 'isin': 'US2810201077'},
            'GILD': {'name': 'Gilead Sciences', 'hauptsitz': 'Foster City, CA, USA', 'branche': 'Biopharmaceuticals', 'beschreibung': 'HIV, Hepatitis & Oncology', 'wkn': '885823', 'isin': 'US3755581036'},
            'REGN': {'name': 'Regeneron Pharmaceuticals', 'hauptsitz': 'Tarrytown, NY, USA', 'branche': 'Biotechnology', 'beschreibung': 'Antibody-based Medicines', 'wkn': '881535', 'isin': 'US75886F1075'},
            'VRTX': {'name': 'Vertex Pharmaceuticals', 'hauptsitz': 'Boston, MA, USA', 'branche': 'Rare Disease Therapies', 'beschreibung': 'Cystic Fibrosis & Rare Diseases', 'wkn': '882807', 'isin': 'US92532F1003'},
            
            # USA Clean Energy mit WKN
            'ENPH': {'name': 'Enphase Energy', 'hauptsitz': 'Fremont, CA, USA', 'branche': 'Solar Technology', 'beschreibung': 'Solar Microinverters & Batterien', 'wkn': 'A1JC82', 'isin': 'US29355A1079'},
            'SEDG': {'name': 'SolarEdge Technologies', 'hauptsitz': 'Herzliya, Israel', 'branche': 'Solar Inverters', 'beschreibung': 'Smart Solar Inverter Systems', 'wkn': 'A14QVM', 'isin': 'US83417M1045'},
            'PLUG': {'name': 'Plug Power Inc.', 'hauptsitz': 'Latham, NY, USA', 'branche': 'Hydrogen Fuel Cells', 'beschreibung': 'Wasserstoff-Brennstoffzellen', 'wkn': 'A1JA81', 'isin': 'US72919P2020'},
            'BE': {'name': 'Bloom Energy Corp.', 'hauptsitz': 'San Jose, CA, USA', 'branche': 'Fuel Cell Technology', 'beschreibung': 'Solid Oxide Fuel Cells', 'wkn': 'A2JQTG', 'isin': 'US0937121079'},
            'FSLR': {'name': 'First Solar Inc.', 'hauptsitz': 'Tempe, AZ, USA', 'branche': 'Solar Panels', 'beschreibung': 'Thin-Film Solar Modules', 'wkn': 'A0LEKM', 'isin': 'US3364331070'},
            'NEL': {'name': 'Nel ASA', 'hauptsitz': 'Oslo, Norwegen', 'branche': 'Hydrogen Technology', 'beschreibung': 'Hydrogen Production & Fueling', 'wkn': 'A0B733', 'isin': 'NO0010081235'},
            
            # USA Gaming & Entertainment mit WKN
            'ROKU': {'name': 'Roku Inc.', 'hauptsitz': 'San Jose, CA, USA', 'branche': 'Streaming Devices', 'beschreibung': 'TV Streaming Platform & Ads', 'wkn': 'A2DW4X', 'isin': 'US77543R1023'},
            'FUBO': {'name': 'fuboTV Inc.', 'hauptsitz': 'New York, NY, USA', 'branche': 'Live TV Streaming', 'beschreibung': 'Sports-first Live TV Streaming', 'wkn': 'A2P6J0', 'isin': 'US35905R1077'},
            'TTWO': {'name': 'Take-Two Interactive', 'hauptsitz': 'New York, NY, USA', 'branche': 'Video Games', 'beschreibung': 'Grand Theft Auto, NBA 2K', 'wkn': '888736', 'isin': 'US8740541094'},
            'EA': {'name': 'Electronic Arts Inc.', 'hauptsitz': 'Redwood City, CA, USA', 'branche': 'Video Games', 'beschreibung': 'FIFA, Madden NFL, Battlefield', 'wkn': '878372', 'isin': 'US2855121099'},
            'ATVI': {'name': 'Activision Blizzard', 'hauptsitz': 'Santa Monica, CA, USA', 'branche': 'Video Games', 'beschreibung': 'Call of Duty, World of Warcraft', 'wkn': 'A0Q4K4', 'isin': 'US00507V1098'},
            
            # E-Commerce mit WKN
            'SHOP': {'name': 'Shopify Inc.', 'hauptsitz': 'Ottawa, Kanada', 'branche': 'E-Commerce Platform', 'beschreibung': 'Online Store Building Platform', 'wkn': 'A14TJP', 'isin': 'CA82509L1076'},
            'ETSY': {'name': 'Etsy Inc.', 'hauptsitz': 'Brooklyn, NY, USA', 'branche': 'Online Marketplace', 'beschreibung': 'Handmade & Vintage Items', 'wkn': 'A14P98', 'isin': 'US29786A1060'},
            'EBAY': {'name': 'eBay Inc.', 'hauptsitz': 'San Jose, CA, USA', 'branche': 'Online Marketplace', 'beschreibung': 'Global E-Commerce Platform', 'wkn': '916529', 'isin': 'US2786421030'},
            
            # EV & Mobility mit WKN
            'NIO': {'name': 'NIO Inc.', 'hauptsitz': 'Shanghai, China', 'branche': 'Electric Vehicles', 'beschreibung': 'Premium Electric SUVs China', 'wkn': 'A2N4PB', 'isin': 'US62914V1061'},
            'XPEV': {'name': 'XPeng Inc.', 'hauptsitz': 'Guangzhou, China', 'branche': 'Smart Electric Vehicles', 'beschreibung': 'AI-powered Electric Cars', 'wkn': 'A2QGGT', 'isin': 'US98422D1054'},
            'LI': {'name': 'Li Auto Inc.', 'hauptsitz': 'Beijing, China', 'branche': 'Extended-Range EVs', 'beschreibung': 'Extended-Range Electric SUVs', 'wkn': 'A2QAJD', 'isin': 'US53218H1068'},
            
            # Space & Defense mit WKN
            'SPCE': {'name': 'Virgin Galactic', 'hauptsitz': 'Las Cruces, NM, USA', 'branche': 'Space Tourism', 'beschreibung': 'Commercial Space Flights', 'wkn': 'A1W2FS', 'isin': 'US92766K1060'},
            'RKLB': {'name': 'Rocket Lab USA', 'hauptsitz': 'Long Beach, CA, USA', 'branche': 'Space Launch', 'beschreibung': 'Small Satellite Launch Services', 'wkn': 'A3CVXJ', 'isin': 'US77501A1025'},
            'ASTR': {'name': 'Astra Space Inc.', 'hauptsitz': 'Alameda, CA, USA', 'branche': 'Launch Services', 'beschreibung': 'Daily Space Launch Services', 'wkn': 'A3C3QN', 'isin': 'US04622T1007'},
            
            # Cannabis mit WKN
            'TLRY': {'name': 'Tilray Brands', 'hauptsitz': 'New York, NY, USA', 'branche': 'Cannabis & Wellness', 'beschreibung': 'Medical & Recreational Cannabis', 'wkn': 'A2JQSC', 'isin': 'US88688T1007'},
            'CGC': {'name': 'Canopy Growth Corp.', 'hauptsitz': 'Smiths Falls, Kanada', 'branche': 'Cannabis Producer', 'beschreibung': 'Cannabis Products & Beverages', 'wkn': 'A140QA', 'isin': 'CA1380351009'},
            'ACB': {'name': 'Aurora Cannabis Inc.', 'hauptsitz': 'Edmonton, Kanada', 'branche': 'Cannabis Production', 'beschreibung': 'Medical & Consumer Cannabis', 'wkn': 'A12GS7', 'isin': 'CA05156X8843'},
            
            # Real Estate Tech mit WKN
            'RDFN': {'name': 'Redfin Corporation', 'hauptsitz': 'Seattle, WA, USA', 'branche': 'Real Estate Technology', 'beschreibung': 'Online Real Estate Platform', 'wkn': 'A2DU22', 'isin': 'US75737F1084'},
            'EXPI': {'name': 'eXp World Holdings', 'hauptsitz': 'Bellingham, WA, USA', 'branche': 'Virtual Real Estate', 'beschreibung': 'Cloud-based Real Estate', 'wkn': 'A2DGZ6', 'isin': 'US30063P1057'},
            'OPEN': {'name': 'Opendoor Technologies', 'hauptsitz': 'San Francisco, CA, USA', 'branche': 'iBuying', 'beschreibung': 'Instant Home Buying Platform', 'wkn': 'A2QEX9', 'isin': 'US68373Q1094'},
            
            # Crypto Mining mit WKN
            'RIOT': {'name': 'Riot Platforms Inc.', 'hauptsitz': 'Castle Rock, CO, USA', 'branche': 'Bitcoin Mining', 'beschreibung': 'Bitcoin Mining Operations', 'wkn': 'A2H51D', 'isin': 'US7672921050'},
            'MARA': {'name': 'Marathon Digital', 'hauptsitz': 'Las Vegas, NV, USA', 'branche': 'Bitcoin Mining', 'beschreibung': 'Digital Asset Technology', 'wkn': 'A2QQBE', 'isin': 'US56553P1049'},
            'CLSK': {'name': 'CleanSpark Inc.', 'hauptsitz': 'Henderson, NV, USA', 'branche': 'Bitcoin Mining', 'beschreibung': 'Sustainable Bitcoin Mining', 'wkn': 'A2QJDK', 'isin': 'US18442Q1013'},
            
            # Food Tech mit WKN
            'BYND': {'name': 'Beyond Meat Inc.', 'hauptsitz': 'El Segundo, CA, USA', 'branche': 'Plant-based Food', 'beschreibung': 'Plant-based Meat Alternatives', 'wkn': 'A2N7XQ', 'isin': 'US08862E1091'},
            'OATS': {'name': 'Oatly Group AB', 'hauptsitz': 'Malmö, Schweden', 'branche': 'Plant-based Dairy', 'beschreibung': 'Oat-based Milk Products', 'wkn': 'A3CQRG', 'isin': 'US67421J1088'},
            
            # Micro-Cap USA mit WKN
            'MVIS': {'name': 'MicroVision Inc.', 'hauptsitz': 'Redmond, WA, USA', 'branche': 'Lidar Technology', 'beschreibung': 'Automotive Lidar & AR Displays', 'wkn': 'A1KCVK', 'isin': 'US5949724083'},
            'VERB': {'name': 'Verb Technology', 'hauptsitz': 'Las Vegas, NV, USA', 'branche': 'Video Marketing', 'beschreibung': 'Interactive Video Platform', 'wkn': 'A2JAEY', 'isin': 'US92537N1081'},
            'FIZZ': {'name': 'National Beverage Corp.', 'hauptsitz': 'Fort Lauderdale, FL, USA', 'branche': 'Beverages', 'beschreibung': 'LaCroix Sparkling Water', 'wkn': '913872', 'isin': 'US6363694071'},
            'GRWG': {'name': 'GrowGeneration Corp.', 'hauptsitz': 'Denver, CO, USA', 'branche': 'Hydroponic Equipment', 'beschreibung': 'Cannabis Growing Supplies', 'wkn': 'A2DKMG', 'isin': 'US39945A1079'},
            
            # Cybersecurity USA/Israel mit WKN
            'S': {'name': 'SentinelOne Inc.', 'hauptsitz': 'Mountain View, CA, USA', 'branche': 'AI Cybersecurity', 'beschreibung': 'AI-powered Endpoint Security', 'wkn': 'A3DAQR', 'isin': 'US81761R1086'},
            'CYBR': {'name': 'CyberArk Software', 'hauptsitz': 'Petah Tikva, Israel', 'branche': 'Privileged Access', 'beschreibung': 'Privileged Access Management', 'wkn': 'A2DKZK', 'isin': 'US23282E1010'},
            'CHKP': {'name': 'Check Point Software', 'hauptsitz': 'Tel Aviv, Israel', 'branche': 'Network Security', 'beschreibung': 'Firewall & Security Solutions', 'wkn': '862851', 'isin': 'IL0010824113'},
            'FTNT': {'name': 'Fortinet Inc.', 'hauptsitz': 'Sunnyvale, CA, USA', 'branche': 'Network Security', 'beschreibung': 'Cybersecurity Solutions', 'wkn': 'A0YEFE', 'isin': 'US34959E1091'},
            
            # Deutsche Aktien
            'SAP': {'name': 'SAP SE', 'hauptsitz': 'Walldorf, Deutschland', 'branche': 'Enterprise Software', 'beschreibung': 'ERP & Business Software', 'wkn': '716460'},
            'BMW': {'name': 'Bayerische Motoren Werke AG', 'hauptsitz': 'München, Deutschland', 'branche': 'Automotive', 'beschreibung': 'Premium Automobiles & Motorcycles', 'wkn': '519000'},
            'MBG': {'name': 'Mercedes-Benz Group AG', 'hauptsitz': 'Stuttgart, Deutschland', 'branche': 'Luxury Automotive', 'beschreibung': 'Luxury Cars & Commercial Vehicles', 'wkn': 'A3BQ6P'},
            'VOW3': {'name': 'Volkswagen AG', 'hauptsitz': 'Wolfsburg, Deutschland', 'branche': 'Automotive', 'beschreibung': 'Mass Market Automobiles', 'wkn': '766403'},
            'ALV': {'name': 'Allianz SE', 'hauptsitz': 'München, Deutschland', 'branche': 'Insurance', 'beschreibung': 'Global Insurance & Asset Management', 'wkn': '840400'},
            'SIE': {'name': 'Siemens AG', 'hauptsitz': 'München, Deutschland', 'branche': 'Industrial Technology', 'beschreibung': 'Automation & Digitalization', 'wkn': '723610'},
            'BAS': {'name': 'BASF SE', 'hauptsitz': 'Ludwigshafen, Deutschland', 'branche': 'Chemicals', 'beschreibung': 'Chemical Products & Solutions', 'wkn': 'BASF11'},
            'BAYN': {'name': 'Bayer AG', 'hauptsitz': 'Leverkusen, Deutschland', 'branche': 'Pharmaceuticals', 'beschreibung': 'Healthcare & Agriculture', 'wkn': 'BAY001'},
            'DTE': {'name': 'Deutsche Telekom AG', 'hauptsitz': 'Bonn, Deutschland', 'branche': 'Telecommunications', 'beschreibung': 'Mobile & Fixed Networks', 'wkn': '555750'},
            'DB1': {'name': 'Deutsche Bank AG', 'hauptsitz': 'Frankfurt, Deutschland', 'branche': 'Investment Banking', 'beschreibung': 'Global Banking & Finance', 'wkn': '514000'},
            'ADS': {'name': 'Adidas AG', 'hauptsitz': 'Herzogenaurach, Deutschland', 'branche': 'Sportswear', 'beschreibung': 'Sports Equipment & Apparel', 'wkn': 'A1EWWW'},
            'ZAL': {'name': 'Zalando SE', 'hauptsitz': 'Berlin, Deutschland', 'branche': 'E-Commerce Fashion', 'beschreibung': 'Online Fashion Platform', 'wkn': 'ZAL111'},
            'IFX': {'name': 'Infineon Technologies AG', 'hauptsitz': 'Neubiberg, Deutschland', 'branche': 'Semiconductors', 'beschreibung': 'Power & Sensor Semiconductors', 'wkn': '623100'},
            'RWE': {'name': 'RWE AG', 'hauptsitz': 'Essen, Deutschland', 'branche': 'Renewable Energy', 'beschreibung': 'Power Generation & Trading', 'wkn': '703712'},
            
            # Niederländische Aktien
            'ASML': {'name': 'ASML Holding NV', 'hauptsitz': 'Veldhoven, Niederlande', 'branche': 'Semiconductor Equipment', 'beschreibung': 'Lithography Systems'},
            'HEIA': {'name': 'Heineken NV', 'hauptsitz': 'Amsterdam, Niederlande', 'branche': 'Beverages', 'beschreibung': 'Premium Beer & Beverages'},
            'UNA': {'name': 'Unilever NV', 'hauptsitz': 'Rotterdam, Niederlande', 'branche': 'Consumer Goods', 'beschreibung': 'Food & Personal Care Products'},
            'ADYEN': {'name': 'Adyen NV', 'hauptsitz': 'Amsterdam, Niederlande', 'branche': 'Payment Technology', 'beschreibung': 'Global Payment Platform'},
            'INGA': {'name': 'ING Groep NV', 'hauptsitz': 'Amsterdam, Niederlande', 'branche': 'Banking', 'beschreibung': 'Digital Banking Services'},
            'BESI': {'name': 'BE Semiconductor Industries', 'hauptsitz': 'Duiven, Niederlande', 'branche': 'Semiconductor Equipment', 'beschreibung': 'Assembly & Test Equipment'},
            
            # Schweizer Aktien
            'NESN': {'name': 'Nestlé SA', 'hauptsitz': 'Vevey, Schweiz', 'branche': 'Food & Beverages', 'beschreibung': 'Global Food & Nutrition', 'wkn': 'A0Q4DC'},
            'NOVN': {'name': 'Novartis AG', 'hauptsitz': 'Basel, Schweiz', 'branche': 'Pharmaceuticals', 'beschreibung': 'Innovative Medicines', 'wkn': '904278'},
            'ROG': {'name': 'Roche Holding AG', 'hauptsitz': 'Basel, Schweiz', 'branche': 'Pharmaceuticals', 'beschreibung': 'Pharmaceuticals & Diagnostics', 'wkn': '851311'},
            'UHR': {'name': 'The Swatch Group AG', 'hauptsitz': 'Biel, Schweiz', 'branche': 'Luxury Goods', 'beschreibung': 'Swiss Watches & Jewelry', 'wkn': '865126'},
            'UBSG': {'name': 'UBS Group AG', 'hauptsitz': 'Zürich, Schweiz', 'branche': 'Investment Banking', 'beschreibung': 'Wealth Management & Banking', 'wkn': 'A12DFH'},
            'ABBN': {'name': 'ABB Ltd', 'hauptsitz': 'Zürich, Schweiz', 'branche': 'Industrial Technology', 'beschreibung': 'Robotics & Automation', 'wkn': '919730'},
            'ZURN': {'name': 'Zurich Insurance Group', 'hauptsitz': 'Zürich, Schweiz', 'branche': 'Insurance', 'beschreibung': 'Property & Casualty Insurance', 'wkn': 'A0M4ZZ'},
            
            # Französische Aktien
            'MC': {'name': 'LVMH Moët Hennessy', 'hauptsitz': 'Paris, Frankreich', 'branche': 'Luxury Goods', 'beschreibung': 'Luxury Fashion & Accessories', 'wkn': '853292'},
            'OR': {'name': "L'Oréal SA", 'hauptsitz': 'Clichy, Frankreich', 'branche': 'Cosmetics', 'beschreibung': 'Beauty & Personal Care', 'wkn': '853888'},
            'TTE': {'name': 'TotalEnergies SE', 'hauptsitz': 'Courbevoie, Frankreich', 'branche': 'Oil & Gas', 'beschreibung': 'Energy & Petrochemicals', 'wkn': '850727'},
            'BNP': {'name': 'BNP Paribas SA', 'hauptsitz': 'Paris, Frankreich', 'branche': 'Banking', 'beschreibung': 'European Banking Leader', 'wkn': '887771'},
            'SAN': {'name': 'Sanofi SA', 'hauptsitz': 'Paris, Frankreich', 'branche': 'Pharmaceuticals', 'beschreibung': 'Global Healthcare', 'wkn': '920657'},
            'AI': {'name': 'Air Liquide SA', 'hauptsitz': 'Paris, Frankreich', 'branche': 'Industrial Gases', 'beschreibung': 'Industrial & Medical Gases', 'wkn': '850133'},
            'KER': {'name': 'Kering SA', 'hauptsitz': 'Paris, Frankreich', 'branche': 'Luxury Fashion', 'beschreibung': 'Gucci, Saint Laurent, Bottega', 'wkn': '851223'},
            'STM': {'name': 'STMicroelectronics NV', 'hauptsitz': 'Genf, Schweiz', 'branche': 'Semiconductors', 'beschreibung': 'Automotive & IoT Chips', 'wkn': 'A0HFHS'},
            
            # Britische Aktien
            'SHEL': {'name': 'Shell plc', 'hauptsitz': 'London, Großbritannien', 'branche': 'Oil & Gas', 'beschreibung': 'Integrated Energy Company', 'wkn': 'A3C99G'},
            'AZN': {'name': 'AstraZeneca PLC', 'hauptsitz': 'Cambridge, Großbritannien', 'branche': 'Pharmaceuticals', 'beschreibung': 'Biopharmaceuticals', 'wkn': '886455'},
            'LSEG': {'name': 'London Stock Exchange Group', 'hauptsitz': 'London, Großbritannien', 'branche': 'Financial Services', 'beschreibung': 'Market Infrastructure', 'wkn': 'A0MZ2U'},
            'ULVR': {'name': 'Unilever PLC', 'hauptsitz': 'London, Großbritannien', 'branche': 'Consumer Goods', 'beschreibung': 'Sustainable Living Brands', 'wkn': 'A0JMZB'},
            'BP': {'name': 'BP p.l.c.', 'hauptsitz': 'London, Großbritannien', 'branche': 'Oil & Gas', 'beschreibung': 'Energy Transition Company', 'wkn': '850517'},
            'GSK': {'name': 'GSK plc', 'hauptsitz': 'London, Großbritannien', 'branche': 'Pharmaceuticals', 'beschreibung': 'Vaccines & Medicines', 'wkn': '940561'},
            'VOD': {'name': 'Vodafone Group Plc', 'hauptsitz': 'Newbury, Großbritannien', 'branche': 'Telecommunications', 'beschreibung': 'Mobile Networks & Services', 'wkn': 'A1XA83'},
            'OCDO': {'name': 'Ocado Group plc', 'hauptsitz': 'Hatfield, Großbritannien', 'branche': 'Online Grocery', 'beschreibung': 'Automated Grocery Solutions', 'wkn': 'A0KBWP'},
            
            # Italienische Aktien
            'ENI': {'name': 'Eni S.p.A.', 'hauptsitz': 'Rom, Italien', 'branche': 'Oil & Gas', 'beschreibung': 'Energy & Petrochemicals', 'wkn': '897791'},
            'ISP': {'name': 'Intesa Sanpaolo', 'hauptsitz': 'Turin, Italien', 'branche': 'Banking', 'beschreibung': 'Italian Banking Leader', 'wkn': 'A0M4WZ'},
            'UCG': {'name': 'UniCredit S.p.A.', 'hauptsitz': 'Mailand, Italien', 'branche': 'Banking', 'beschreibung': 'Pan-European Banking', 'wkn': 'A2DYJN'},
            'RACE': {'name': 'Ferrari N.V.', 'hauptsitz': 'Maranello, Italien', 'branche': 'Luxury Automotive', 'beschreibung': 'Luxury Sports Cars', 'wkn': 'A2ACKK'},
            'ENEL': {'name': 'Enel S.p.A.', 'hauptsitz': 'Rom, Italien', 'branche': 'Utilities', 'beschreibung': 'Renewable Energy & Utilities', 'wkn': '928624'},
            
            # Spanische Aktien
            'ITX': {'name': 'Industria de Diseño Textil', 'hauptsitz': 'A Coruña, Spanien', 'branche': 'Fashion Retail', 'beschreibung': 'Zara, Massimo Dutti, Pull&Bear', 'wkn': 'A0N7XF'},
            'IBE': {'name': 'Iberdrola SA', 'hauptsitz': 'Bilbao, Spanien', 'branche': 'Renewable Energy', 'beschreibung': 'Wind & Solar Power', 'wkn': 'A0M46B'},
            'TEF': {'name': 'Telefónica SA', 'hauptsitz': 'Madrid, Spanien', 'branche': 'Telecommunications', 'beschreibung': 'Latin American Telecom', 'wkn': '850775'},
            'BBVA': {'name': 'Banco Bilbao Vizcaya', 'hauptsitz': 'Bilbao, Spanien', 'branche': 'Banking', 'beschreibung': 'Digital Banking Solutions', 'wkn': '875773'},
            'REP': {'name': 'Repsol SA', 'hauptsitz': 'Madrid, Spanien', 'branche': 'Oil & Gas', 'beschreibung': 'Energy & Petrochemicals', 'wkn': '876845'},
            
            # Norwegische Aktien
            'EQNR': {'name': 'Equinor ASA', 'hauptsitz': 'Stavanger, Norwegen', 'branche': 'Oil & Gas', 'beschreibung': 'Offshore Energy & Renewables', 'wkn': 'A0ERZ1'},
            'MOWI': {'name': 'Mowi ASA', 'hauptsitz': 'Bergen, Norwegen', 'branche': 'Aquaculture', 'beschreibung': 'Atlantic Salmon Farming', 'wkn': 'A115CA'},
            'NEL': {'name': 'Nel ASA', 'hauptsitz': 'Oslo, Norwegen', 'branche': 'Hydrogen Technology', 'beschreibung': 'Hydrogen Production & Fueling', 'wkn': 'A0B733'},
            'YAR': {'name': 'Yara International ASA', 'hauptsitz': 'Oslo, Norwegen', 'branche': 'Fertilizers', 'beschreibung': 'Crop Nutrition Solutions', 'wkn': 'A0CA25'},
            
            # Schwedische Aktien
            'ERICB': {'name': 'Telefonaktiebolaget LM Ericsson', 'hauptsitz': 'Stockholm, Schweden', 'branche': '5G Technology', 'beschreibung': '5G Networks & Infrastructure', 'wkn': '850001'},
            'VOLV-B': {'name': 'Volvo AB', 'hauptsitz': 'Göteborg, Schweden', 'branche': 'Commercial Vehicles', 'beschreibung': 'Trucks & Construction Equipment', 'wkn': '889049'},
            'SAND': {'name': 'Sandvik AB', 'hauptsitz': 'Stockholm, Schweden', 'branche': 'Industrial Tools', 'beschreibung': 'Mining & Manufacturing Tools', 'wkn': '870023'},
            
            # Dänische Aktien
            'NOVO-B': {'name': 'Novo Nordisk A/S', 'hauptsitz': 'Bagsværd, Dänemark', 'branche': 'Diabetes Care', 'beschreibung': 'Diabetes & Obesity Treatment', 'wkn': 'A1XA8R'},
            'ORSTED': {'name': 'Ørsted A/S', 'hauptsitz': 'Fredericia, Dänemark', 'branche': 'Offshore Wind', 'beschreibung': 'Offshore Wind Energy', 'wkn': 'A0NBLH'},
            'MAERSK-B': {'name': 'A.P. Møller-Mærsk', 'hauptsitz': 'Kopenhagen, Dänemark', 'branche': 'Shipping & Logistics', 'beschreibung': 'Container Shipping & Ports', 'wkn': '861837'},
            'DSV': {'name': 'DSV A/S', 'hauptsitz': 'Hedehusene, Dänemark', 'branche': 'Logistics', 'beschreibung': 'Global Transport & Logistics', 'wkn': 'A0KFYR'},
            
            # Finnische Aktien
            'NOKIA': {'name': 'Nokia Corporation', 'hauptsitz': 'Espoo, Finnland', 'branche': '5G Technology', 'beschreibung': '5G Networks & Mobile Technology', 'wkn': '870737'},
            'NESTE': {'name': 'Neste Corporation', 'hauptsitz': 'Espoo, Finnland', 'branche': 'Renewable Fuels', 'beschreibung': 'Sustainable Aviation Fuel', 'wkn': 'A1XB9T'},
            'UPM': {'name': 'UPM-Kymmene Corporation', 'hauptsitz': 'Helsinki, Finnland', 'branche': 'Forest Products', 'beschreibung': 'Sustainable Forest Solutions', 'wkn': '869257'},
            'FORTUM': {'name': 'Fortum Corporation', 'hauptsitz': 'Espoo, Finnland', 'branche': 'Clean Energy', 'beschreibung': 'Clean Energy Solutions', 'wkn': '598200', 'isin': 'FI0009007132'},
        
            # CHINA - Major Tech & Growth Stocks mit WKN
            'BABA': {'name': 'Alibaba Group Holding', 'hauptsitz': 'Hangzhou, China', 'branche': 'E-Commerce & Cloud', 'beschreibung': 'Chinas größte E-Commerce-Plattform', 'wkn': 'A117ME', 'isin': 'US01609W1027'},
            'JD': {'name': 'JD.com Inc.', 'hauptsitz': 'Beijing, China', 'branche': 'E-Commerce', 'beschreibung': 'Online Retail & Logistics', 'wkn': 'A112ST', 'isin': 'US47215P1066'},
            'PDD': {'name': 'PDD Holdings', 'hauptsitz': 'Shanghai, China', 'branche': 'Social Commerce', 'beschreibung': 'Group Buying Platform Pinduoduo', 'wkn': 'A2JRK6', 'isin': 'US69608A2084'},
            'BIDU': {'name': 'Baidu Inc.', 'hauptsitz': 'Beijing, China', 'branche': 'Internet Search & AI', 'beschreibung': 'Chinese Search Engine & AI', 'wkn': 'A0F5DE', 'isin': 'US0567521085'},
            'NTES': {'name': 'NetEase Inc.', 'hauptsitz': 'Hangzhou, China', 'branche': 'Online Gaming', 'beschreibung': 'Mobile & PC Gaming', 'wkn': '913810', 'isin': 'US64110W1027'},
            'TME': {'name': 'Tencent Music Entertainment', 'hauptsitz': 'Shenzhen, China', 'branche': 'Music Streaming', 'beschreibung': 'QQ Music, Kugou, Kuwo', 'wkn': 'A2PJ6J', 'isin': 'US88034P1093'},
            'BILI': {'name': 'Bilibili Inc.', 'hauptsitz': 'Shanghai, China', 'branche': 'Video Platform', 'beschreibung': 'Chinese YouTube for Gen Z', 'wkn': 'A2PGJ7', 'isin': 'US0900171014'},
            'DIDI': {'name': 'Didi Global Inc.', 'hauptsitz': 'Beijing, China', 'branche': 'Ride-Hailing', 'beschreibung': 'Chinese Uber', 'wkn': 'A3C9Y7', 'isin': 'US25401A1079'},
            'BEKE': {'name': 'KE Holdings Inc.', 'hauptsitz': 'Beijing, China', 'branche': 'Real Estate Services', 'beschreibung': 'Property Transaction Platform', 'wkn': 'A2QFZP', 'isin': 'US4873804048'},
            
            # ASIEN - Japan Major Stocks mit WKN
            'TSM': {'name': 'Taiwan Semiconductor', 'hauptsitz': 'Hsinchu, Taiwan', 'branche': 'Semiconductor Manufacturing', 'beschreibung': 'Weltweit größter Chipfertiger', 'wkn': '909800', 'isin': 'US8740391003'},
            'SONY': {'name': 'Sony Group Corporation', 'hauptsitz': 'Tokyo, Japan', 'branche': 'Consumer Electronics', 'beschreibung': 'PlayStation, Music, Movies', 'wkn': '853687', 'isin': 'US8356993076'},
            'TM': {'name': 'Toyota Motor Corporation', 'hauptsitz': 'Toyota, Japan', 'branche': 'Automotive', 'beschreibung': 'Hybrid & Electric Vehicles', 'wkn': '853510', 'isin': 'US8923561067'},
            'FAST': {'name': 'Fast Retailing Co.', 'hauptsitz': 'Yamaguchi, Japan', 'branche': 'Apparel Retail', 'beschreibung': 'Uniqlo Fashion Brand', 'wkn': 'A0MXDJ', 'isin': 'JP3802300008'},
            
            # ASIEN - Südkorea mit WKN
            'SE': {'name': 'Sea Limited', 'hauptsitz': 'Singapur', 'branche': 'Gaming & E-Commerce', 'beschreibung': 'Shopee, Garena Free Fire', 'wkn': 'A2H5LX', 'isin': 'US81141R1005'},
            
            # ASIEN - Indien mit WKN
            'INFY': {'name': 'Infosys Limited', 'hauptsitz': 'Bangalore, Indien', 'branche': 'IT Services', 'beschreibung': 'Software Development & Consulting', 'wkn': '919804', 'isin': 'US4567881085'},
            'WIT': {'name': 'Wipro Limited', 'hauptsitz': 'Bangalore, Indien', 'branche': 'IT Services', 'beschreibung': 'Digital Transformation Services', 'wkn': 'A0MQQ4', 'isin': 'US97651K1025'},
            
            # LATEINAMERIKA mit WKN
            'MELI': {'name': 'MercadoLibre Inc.', 'hauptsitz': 'Buenos Aires, Argentinien', 'branche': 'E-Commerce Latin America', 'beschreibung': 'E-Commerce & Fintech Platform', 'wkn': 'A0MYNP', 'isin': 'US58733R1023'},
            'GLOB': {'name': 'Globant S.A.', 'hauptsitz': 'Buenos Aires, Argentinien', 'branche': 'Software Development', 'beschreibung': 'Digital Solutions & Services', 'wkn': 'A12BK6', 'isin': 'LU1377946853'},
            'STNE': {'name': 'StoneCo Ltd.', 'hauptsitz': 'São Paulo, Brasilien', 'branche': 'Fintech Brazil', 'beschreibung': 'Payment Solutions Brazil', 'wkn': 'A2N7XL', 'isin': 'BMG8589J1051'},
            'PAGS': {'name': 'PagSeguro Digital', 'hauptsitz': 'São Paulo, Brasilien', 'branche': 'Digital Payments', 'beschreibung': 'Brazilian Payment Platform', 'wkn': 'A2H9WU', 'isin': 'BMG6839V1081'},
            'VTEX': {'name': 'VTEX S.A.', 'hauptsitz': 'Rio de Janeiro, Brasilien', 'branche': 'E-Commerce Platform', 'beschreibung': 'Enterprise E-Commerce Solutions', 'wkn': 'A3C6N3', 'isin': 'US92913X1019'},
            
            # AUSTRALIEN mit WKN
            'CSL': {'name': 'CSL Limited', 'hauptsitz': 'Melbourne, Australien', 'branche': 'Biotechnology', 'beschreibung': 'Blood Plasma Products', 'wkn': '884981', 'isin': 'AU000000CSL8'},
            'BHP': {'name': 'BHP Group Limited', 'hauptsitz': 'Melbourne, Australien', 'branche': 'Mining', 'beschreibung': 'Iron Ore & Copper Mining', 'wkn': '850524', 'isin': 'AU000000BHP4'},
            'CBA': {'name': 'Commonwealth Bank', 'hauptsitz': 'Sydney, Australien', 'branche': 'Banking', 'beschreibung': 'Major Australian Bank', 'wkn': '851767', 'isin': 'AU000000CBA7'},
            
            # ISRAEL Tech mit WKN
            'WDAY': {'name': 'Workday Inc.', 'hauptsitz': 'Pleasanton, CA, USA', 'branche': 'Enterprise Software', 'beschreibung': 'HR & Financial Management', 'wkn': 'A1W309', 'isin': 'US98138H1014'},
            'MNDY': {'name': 'monday.com Ltd.', 'hauptsitz': 'Tel Aviv, Israel', 'branche': 'Work Management', 'beschreibung': 'Team Collaboration Platform', 'wkn': 'A3C2BL', 'isin': 'IL0011301780'},
            'FVRR': {'name': 'Fiverr International', 'hauptsitz': 'Tel Aviv, Israel', 'branche': 'Freelance Marketplace', 'beschreibung': 'Gig Economy Platform', 'wkn': 'A2PLU5', 'isin': 'US33812L1089'},
            'WIX': {'name': 'Wix.com Ltd.', 'hauptsitz': 'Tel Aviv, Israel', 'branche': 'Website Building', 'beschreibung': 'Website Creation Platform', 'wkn': 'A1W4K9', 'isin': 'IL0011301795'},
            'NICE': {'name': 'NICE Ltd.', 'hauptsitz': 'Ra\'anana, Israel', 'branche': 'Customer Analytics', 'beschreibung': 'Customer Experience Software', 'wkn': '885053', 'isin': 'US6542721050'},
            
            # AFRICAN MARKETS mit WKN (soweit verfügbar)
            'NPN': {'name': 'Naspers Limited', 'hauptsitz': 'Kapstadt, Südafrika', 'branche': 'Internet & Media', 'beschreibung': 'Tencent Investor, Media Group', 'wkn': 'A1JDGX', 'isin': 'ZAE000015889'},
            'PRX': {'name': 'Prosus N.V.', 'hauptsitz': 'Amsterdam, Niederlande', 'branche': 'Internet Investments', 'beschreibung': 'Naspers Internet Assets', 'wkn': 'A2PFZS', 'isin': 'NL0012044747'},
        
        }
        
        # Standard-Profil mit WKN-Generation für unbekannte Symbole
        if symbol in aktien_profile:
            return aktien_profile[symbol]
        else:
            # Generiere automatisch WKN für unbekannte Symbole
            generated_wkn = self.generate_wkn_for_unknown_symbol(symbol)
            return {
                'name': f'{symbol} Corporation',
                'hauptsitz': 'International',
                'branche': 'Growth Technology',
                'beschreibung': 'Emerging Growth Company',
                'wkn': generated_wkn,
                'isin': f'UNKNOWN{symbol[:6]}'
            }
            
    def generate_wkn_for_unknown_symbol(self, symbol: str) -> str:
        """Generiert eine synthetische WKN für unbekannte Symbole"""
        import hashlib
        hash_obj = hashlib.md5(symbol.encode())
        hash_hex = hash_obj.hexdigest()
        # Erstelle 6-stellige WKN aus Hash
        wkn_chars = ''.join([c for c in hash_hex if c.isalnum()])[:6].upper()
        return f'G{wkn_chars[:5]}'  # G für 'Generated'

    def hole_top_10_wachstums_aktien(self) -> List[Dict[str, Any]]:
        """Hauptfunktion: Gibt die Top 10 Wachstumsaktien zurück"""
        alle_ergebnisse = self.analysiere_alle_aktien()
        
        # Top 10 auswählen
        top_10 = alle_ergebnisse[:10]
        
        # Füge Steckbriefe hinzu
        for aktie in top_10:
            steckbrief = self.erstelle_aktien_steckbrief(aktie['symbol'])
            aktie.update(steckbrief)
        
        logger.info("TOP 10 WACHSTUMSAKTIEN:")
        for i, aktie in enumerate(top_10, 1):
            logger.info(f"{i}. {aktie['symbol']} ({aktie['name'][:30]}...): Score {aktie['wachstums_score']}")
        
        return top_10

def main():
    """Test-Funktion"""
    predictor = WachstumsPredictor()
    top_10 = predictor.hole_top_10_wachstums_aktien()
    
    print("\n" + "="*90)
    print("🚀 TOP 10 WACHSTUMSAKTIEN FÜR DIE NÄCHSTEN 30 TAGE 🚀")
    print("="*90)
    
    for i, aktie in enumerate(top_10, 1):
        prognose = aktie['prognose_30_tage']
        print(f"\n{i}. {aktie['symbol']} - {aktie['name']}")
        print(f"   📍 Hauptsitz: {aktie['hauptsitz']}")
        print(f"   🏭 Branche: {aktie['branche']}")
        print(f"   📋 Beschreibung: {aktie['beschreibung']}")
        print(f"   💰 Aktueller Preis: €{aktie['current_price']}")
        print(f"   🎯 Wachstums-Score: {aktie['wachstums_score']}/100")
        print(f"   📈 30-Tage Prognose: €{prognose['prognostizierter_preis']} ({prognose['erwartete_rendite_prozent']:+.2f}%)")
        print(f"   ⚖️ Vertrauen: {prognose['vertrauen_level']} | 🔥 Risiko: {prognose['risiko_level']}")
    
    return top_10

if __name__ == "__main__":
    main()