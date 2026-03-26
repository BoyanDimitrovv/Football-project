from services.club_service import ClubsService
from services.player_service import PlayersService
from services.transfers_service import TransfersService
from utils.logger import log_command

class Router:
    """Клас, който насочва командите към правилния service"""
    
    def __init__(self):
        """Инициализира всички services"""
        self.clubs_service = ClubsService()
        self.players_service = PlayersService()
        self.transfers_service = TransfersService()
    
    def route(self, intent, params, raw_input):
        """
        Насочва заявката към съответния service
        
        Args:
            intent (str): Разпознатото намерение
            params (dict): Параметри извлечени от командата
            raw_input (str): Оригиналното съобщение от потребителя
        
        Returns:
            str: Отговор от съответния service
        """
        
        result = None
        status = "OK"
        
        try:
            # ----- ПОМОЩ -----
            if intent == 'help':
                result = self._get_help()
            
            # ----- ИЗХОД -----
            elif intent == 'exit':
                result = "Довиждане! 👋"
            
            # ----- КЛУБОВЕ -----
            elif intent == 'add_club':
                club_name = params.get('club', '')
                result = self.clubs_service.add_club(club_name)
            
            elif intent == 'list_clubs':
                clubs = self.clubs_service.get_all_clubs()
                if not clubs:
                    result = "📋 Няма добавени клубове."
                else:
                    response = "🏆 Списък с клубове:\n"
                    for club in clubs:
                        response += f"  🏆 {club['id']}. {club['name']}\n"
                    result = response
            
            # ----- ИГРАЧИ -----
            elif intent == 'list_players':
                club_input = params.get('club', '').replace('клуб ', '').strip()
                
                # Проверка за точен клуб без значение главни/малки букви
                all_clubs = self.clubs_service.get_all_clubs()
                club_name = None
                for c in all_clubs:
                    if c['name'].lower() == club_input.lower():
                        club_name = c['name']
                        break
                
                if club_name is None:
                    result = f"❌ Клуб '{club_input}' не съществува"
                else:
                    players, club = self.players_service.get_players_by_club(club_name)
                    if not players:
                        result = f"📋 Няма играчи в {club}"
                    else:
                        response = f"📋 Играчи на {club}:\n"
                        emoji = {'GK': '🧤', 'DF': '🛡️', 'MF': '⚙️', 'FW': '⚽'}
                        status_emoji = {'active': '✅', 'injured': '🤕', 'suspended': '⛔'}
                        # премахване на дублирани играчи
                        unique_players = {p['id']: p for p in players}.values()
                        for player in unique_players:
                            response += (f"  {emoji.get(player['position'], '⚽')} {player['number']}. "
                                         f"{player['full_name']} ({player['nationality']}) "
                                         f"{status_emoji.get(player['status'], '❓')}\n")
                        result = response
            
            # ----- ТРАНСФЕРИ -----
            elif intent == 'transfer_player':
                result = self.transfers_service.transfer_player(
                    player_name=params.get('player', ''),
                    from_club_name=params.get('from_club', ''),
                    to_club_name=params.get('to_club', ''),
                    date_str=params.get('date', ''),
                    fee_str=params.get('fee', None)
                )
            
            elif intent == 'show_transfers_player':
                result = self.transfers_service.list_transfers_by_player(
                    player_name=params.get('player', '')
                )
            
            elif intent == 'show_transfers_club':
                result = self.transfers_service.list_transfers_by_club(
                    club_name=params.get('club', '')
                )
            
            # ----- НЕПОЗНАТА КОМАНДА -----
            else:
                result = "❓ Не разбирам командата. Напишете 'помощ' за списък с команди."
        
        except Exception as e:
            status = "ERROR"
            result = f"❌ Грешка: {str(e)}"
        
        # Логване на командата
        log_command(raw_input, intent, params, result, status)
        
        return result
    
    def _get_help(self):
        """Връща помощно съобщение"""
        return """
╔════════════════════════════════════════════════════════════╗
║                    🏆 НАЛИЧНИ КОМАНДИ 🏆                    ║
╚════════════════════════════════════════════════════════════╝

🏁 КЛУБОВЕ (ЕТАП 2):
────────────────────────────────────────────────────────────
• добави клуб [име]                    - добавя нов клуб
• покажи клубове                        - списък на всички клубове

⚽ ИГРАЧИ (ЕТАП 3):
────────────────────────────────────────────────────────────
• покажи играчи на [КЛУБ]               - списък на играчите в клуб

🔄 ТРАНСФЕРИ (ЕТАП 4 - НОВО):
────────────────────────────────────────────────────────────
• трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА]
  - извършва трансфер на играч
• трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА] сума [ЧИСЛО]
  - трансфер със сума
• покажи трансфери на [ИГРАЧ]
  - история на трансферите на играч
• покажи трансфери на клуб [КЛУБ]
  - входящи трансфери в клуб

❓ ДРУГИ:
────────────────────────────────────────────────────────────
• помощ                                 - показва това меню
• изход                                 - излиза от програмата

📌 ПРИМЕРИ:
• трансфер Пламен Андреев от Левски София в ЦСКА София 2026-03-10
• трансфер Пламен Андреев от ЦСКА София в Лудогорец 2026-03-15 сума 500000
• покажи трансфери на Пламен Андреев
• покажи трансфери на клуб Лудогорец
"""
