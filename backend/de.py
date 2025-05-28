    def init_graph(self):
        """初始化基础知识图谱数据"""
        if not self.driver:
            raise Neo4jError("Neo4j连接未初始化")
        
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    # 清空现有数据
                    tx.run("MATCH (n) DETACH DELETE n")
                    
                    csv_file = Path('static/File/小麦病害信息.csv')
                    if not csv_file.exists():
                        raise Neo4jError(f"CSV文件不存在: {csv_file}")
                    
                    processed_count = 0
                    error_count = 0
                    
                    with open(csv_file, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            try:
                                if self._validate_csv_data(row):
                                    self._process_disease_row(tx, row)
                                    processed_count += 1
                                else:
                                    error_count += 1
                                    logger.warning(f"跳过无效数据行: {row}")
                            except Exception as e:
                                error_count += 1
                                logger.error(f"处理数据行失败: {str(e)}")
                    
                    logger.info(f"数据导入完成: 成功 {processed_count} 条，失败 {error_count} 条")
                    return True
                
        except Exception as e:
            raise Neo4jError(f"初始化知识图谱失败: {str(e)}")