from src.services.clubs_service import ClubsService
from src.services.players_service import PlayersService
from src.services.transfers_service import TransfersService
from src.utils.logger import log_command

class Router:
    """Клас, който насочва командите към правилния service"""
    
    def __init__(self):
        """Инициализира всички services"""
        self.clubs_service = ClubsService()
        self.players_service = PlayersService()
        self.transfers_service = TransfersService()  # Ново за Етап 4
    
    def route(self, intent, params, raw_input):
        """
        Насочва заявката към съответния service
        
        Args:
            intent (str): Разпознатото намерение (help, exit, add_club, etc.)
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
            
            # ----- КЛУБОВЕ (от Етап 2) -----
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
            
            # ----- ИГРАЧИ (от Етап 3) -----
            elif intent == 'list_players':
                club_name = params.get('club', '')
                players, club = self.players_service.get_players_by_club(club_name)
                
                if players is None:
                    result = club  # това е съобщението за грешка
                elif not players:
                    result = f"📋 Няма играчи в {club}"
                else:
                    response = f"📋 Играчи на {club}:\n"
                    # Емоджита за различните позиции
                    emoji = {'GK': '🧤', 'DF': '🛡️', 'MF': '⚙️', 'FW': '⚽'}
                    # Емоджита за статус
                    status_emoji = {'active': '✅', 'injured': '🤕', 'suspended': '⛔'}
                    
                    for player in players:
                        response += (f"  {emoji[player['position']]} {player['number']}. "
                                   f"{player['full_name']} ({player['nationality']}) "
                                   f"{status_emoji[player['status']]}\n")
                    result = response
            
            # ----- 🔄 ТРАНСФЕРИ (НОВО за Етап 4) -----
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
        
        # Логване на командата (използваме новия logger)
        log_command(raw_input, intent, params, result, status)
        
        return result
    
    def _get_help(self):
        """Връща помощно съобщение с всички команди"""
        return """
╔════════════════════════════════════════════════════════════╗
║                    🏆 НАЛИЧНИ КОМАНДИ 🏆                    ║
╚════════════════════════════════════════════════════════════╝

🏁 КЛУБОВЕ (ЕТАП 2):
────────────────────────────────────────────────────────────
• добави клуб [име]                    - добавя нов клуб
  Пример: добави клуб Левски София

• покажи клубове                        - списък на всички клубове
  Пример: покажи клубове

⚽ ИГРАЧИ (ЕТАП 3):
────────────────────────────────────────────────────────────
• покажи играчи на [КЛУБ]               - списък на играчите в клуб
  Пример: покажи играчи на Левски София

🔄 ТРАНСФЕРИ (ЕТАП 4 - НОВО):
────────────────────────────────────────────────────────────
• трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА]
  - извършва трансфер на играч
  Пример: трансфер Пламен Андреев от Левски София в ЦСКА София 2026-03-10

• трансфер [ИГРАЧ] от [ОТ] в [КЪМ] [ДАТА] сума [ЧИСЛО]
  - трансфер със сума
  Пример: трансфер Пламен Андреев от ЦСКА София в Лудогорец 2026-03-15 сума 500000

• покажи трансфери на [ИГРАЧ]
  - история на трансферите на играч
  Пример: покажи трансфери на Пламен Андреев

• покажи трансфери на клуб [КЛУБ]
  - входящи трансфери в клуб
  Пример: покажи трансфери на клуб Лудогорец

❓ ДРУГИ:
────────────────────────────────────────────────────────────
• помощ                                 - показва това меню
• изход                                 - излиза от програмата

╔════════════════════════════════════════════════════════════╗
║  📌 ЗА ДА РАБОТЯТ КОМАНДИТЕ, ПЪРВО ПУСНЕТЕ:               ║
║     python src/seed_data.py                                ║
╚════════════════════════════════════════════════════════════╝
"""
