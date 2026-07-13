from analysis.phoenix_analyzer import PhoenixAnalyzer


class MarketPipeline:

    def __init__(self):

        self.analyzer = PhoenixAnalyzer()


    def run(self, asset):

        print("🦅 Phoenix Market Pipeline Starting...")
        
        report = self.analyzer.run(asset)

        print("✅ Analysis Completed")

        return report