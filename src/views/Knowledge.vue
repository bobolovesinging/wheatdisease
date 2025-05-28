<template>
  <div class="knowledge-container">
    <div class="knowledge-wrapper">
      <!-- 顶部控制栏 -->
      <div class="control-panel">
        <h3>小麦病害知识图谱</h3>
        <!-- 搜索节点区域 -->
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索节点..."
            prefix-icon="el-icon-search"
            clearable
            @input="handleSearch"
            @keyup.enter.native="handleSearchEnter"
          />
        </div>
      </div>
      
      <!-- 添加一个重置按钮 -->
      <el-button 
        v-if="isSubgraphMode" 
        @click="handleResetView" 
        type="primary" 
        size="small"
        style="position: absolute; top: 20px; right: 20px;"
      >
        重置视图
      </el-button>
      
      <!-- 图谱展示区域 --> <!-- dragover.prevent 阻止默认拖拽  drop.prevent 事件处理拖拽放置事件 -->
      <div 
        class="graph-container" 
        ref="graphContainer"
        @dragover.prevent
        @drop.prevent="handleDrop"
      >
        <!-- 这里将渲染知识图谱 -->
        </div>
        
      <!-- 节点详情侧边栏 -->
      <el-drawer
        title="详细信息"
        :visible.sync="drawerVisible"
        direction="rtl"
        size="30%"
        @closed="handleDrawerClose"
      >
        <div v-if="selectedNode" class="node-details">
          <h3>{{ selectedNode.name }}</h3>
          
          <div class="detail-item">
            <label>类型：</label>
            <span>{{ selectedNode.type }}</span>
          </div>

          <!-- Disease节点的详细信息 -->
          <template v-if="selectedNode.type === 'disease' && selectedNode.details">
            <div class="detail-section">
              <div class="detail-item" v-if="selectedNode.details.alias">
                <label>别名：</label>
                <span>{{ selectedNode.details.alias }}</span>
              </div>
              
              <div class="detail-item" v-if="selectedNode.details.pathogen">
                <label>病原：</label>
                <div class="detail-content">{{ selectedNode.details.pathogen }}</div>
              </div>
              
              <div class="detail-item" v-if="selectedNode.details.symptoms">
                <label>症状：</label>
                <div class="detail-content">{{ selectedNode.details.symptoms }}</div>
              </div>
              
              <div class="detail-item" v-if="selectedNode.details.treatment">
                <label>防治：</label>
                <div class="detail-content">{{ selectedNode.details.treatment }}</div>
              </div>
            </div>
          </template>
        </div>
      </el-drawer>
    </div>
  </div>
</template>

<script>
// @ts-ignore
import * as d3 from 'd3';
import axios from 'axios';

export default {
  name: 'KnowledgeView',
  
  data() {
    return {
      searchQuery: '', // 搜索查询字符串
      drawerVisible: false, // 节点详情侧边栏是否可见
      selectedNode: null, // 当前选中的节点
      graph: null, // 图谱实例
      simulation: null, // 力导向图模拟实例
      svg: null, // SVG元素实例
      graphData: null, // 图谱数据
      isDragMode: false, // 是否处于拖拽模式
      nodeTypes: {
        'disease': '#2C3E50', // 黑色系 - 病害
        'weather': '#3498DB', // 蓝色系 - 气象
        'region': '#E67E22', // 橙色系 - 地区
        'plant_part': '#27AE60', // 绿色系 - 部位
        'symptom': '#4ECDC4', // 症状节点 - 青色 
        'cause': '#45B7D1', // 病因节点 - 蓝色
        'treatment': '#96CEB4', // 治疗节点 - 绿色
        'pest': '#FFA07A', // 害虫节点 - 橙色
        'area': '#DDA0DD', // 区域节点 - 紫色
        'morphology': '#87CEEB', // 形态节点 - 天蓝色
        'habit': '#98FB98', // 习性节点 - 浅绿色
        'enemy': '#FFD700', // 天敌节点 - 金色
      },
      isSubgraphMode: false, // 是否处于子图模式
      fullGraphData: null, // 保存完整的图数据
      subgraphCache: new Map(), // 添加缓存对象
    };
  },

  // 组件挂载时执行
  mounted() {
    // 获取图谱数据
    this.fetchGraphData();
    // 添加窗口大小变化的监听器
    window.addEventListener('resize', this.handleResize);
  },

  // 组件销毁前执行
  beforeDestroy() {
    // 清除缓存
    this.subgraphCache.clear();
    // 移除窗口大小变化的监听器,避免内存泄漏
    window.removeEventListener('resize', this.handleResize);
  },

  methods: {
    async fetchGraphData() {
      try {
        const response = await axios.get('/api/knowledge/graph/');
        console.log('获取到的原始响应:', response);
        console.log('图谱数据:', response.data);
        this.graphData = response.data;
        console.log('处理后的graphData:', this.graphData);
        this.initGraph();
      } catch (error) {
        console.error('\n 获取图谱数据失败: ', error);
        console.error('\n 错误响应: ', error.response?.data);
        if (error.response) {
          console.error('错误响应:', error.response);
          this.$message.error(`获取数据失败: ${error.response.data.error || '服务器错误'}`);
        } else if (error.request) {
          this.$message.error('无法连接到服务器，请检查服务器是否运行');
        } else {
          this.$message.error(`请求错误: ${error.message}`);
        }
      }
    },

    // 初始化图谱
    async initGraph() {
      try {
        const response = await axios.get('/api/knowledge/graph/')
        this.fullGraphData = response.data
        this.renderGraph(response.data)
      } catch (error) {
        console.error('获取知识图谱数据失败:', error)
      }
    },

    // 拖拽开始事件处理
    dragstarted(event, d) {
      if (!event.active) this.simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    },

    // 拖拽过程中事件处理
    dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    },

    // 拖拽结束事件处理
    dragended(event, d) {
      if (!event.active) this.simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    },

    // 窗口大小变化事件处理
    handleResize() {
      if (this.svg) {
        const container = this.$refs.graphContainer;
        this.svg
          .attr('width', container.clientWidth)
          .attr('height', container.clientHeight);
        
        this.simulation
          .force('center', d3.forceCenter(
            container.clientWidth / 2, 
            container.clientHeight / 2
          ));
      }
    },

    // 搜索节点事件处理
    handleSearch() {
      if (!this.searchQuery) {
        // 重置所有节点的样式
        this.svg.selectAll('circle')
          .attr('stroke-width', 0)
          .attr('stroke', null);
        return;
      }

      // 高亮匹配的节点
      this.svg.selectAll('circle')
        .attr('stroke-width', d => 
          d.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ? 3 : 0
        )
        .attr('stroke', '#f39c12');
    },

    // 新增：回车时搜索并定位
    handleSearchEnter() {
      if (!this.searchQuery) return;
      const found = this.graphData && this.graphData.nodes && this.graphData.nodes.find(
        n => n.name.toLowerCase() === this.searchQuery.toLowerCase()
      );
      if (found) {
        // 高亮
        this.svg.selectAll('circle')
          .attr('stroke-width', d => d.name.toLowerCase() === this.searchQuery.toLowerCase() ? 5 : 0)
          .attr('stroke', '#f39c12');
        // 平移到中心
        if (found.x !== undefined && found.y !== undefined) {
          const container = this.$refs.graphContainer;
          const width = container.clientWidth;
          const height = container.clientHeight;
          // 计算平移量
          const dx = width / 2 - found.x;
          const dy = height / 2 - found.y;
          // 用d3的zoom平移svg内容
          const zoom = d3.zoom().scaleExtent([0.1, 4]);
          this.svg.transition().duration(500).call(
            zoom.transform,
            d3.zoomIdentity.translate(dx, dy)
          );
        }
      } else {
        this.$message.warning('节点不存在');
      }
    },

    // 节点点击事件处理
    handleNodeClick(node) {
      this.selectedNode = node;
      this.drawerVisible = true;
    },

    // 修改节点点击事件处理
    async showNodeSubgraph(nodeId, nodeType) {
      try {
        let subgraphData;
        const cacheKey = `${nodeType}-${nodeId}`;
        
        // 检查缓存中是否有数据
        if (this.subgraphCache.has(cacheKey)) {
          console.log('从缓存获取子图数据');
          subgraphData = this.subgraphCache.get(cacheKey);
        } else {
          console.log('从后端获取子图数据');
          let response;
          if (nodeType === 'disease') {
            // 获取disease节点的子图
            response = await axios.get(`/api/knowledge/get_disease_subgraph/?disease=${nodeId}`);
          } else {
            // 获取非disease节点的子图
            response = await axios.get(`/api/knowledge/get_node_subgraph/?node=${nodeId}&type=${nodeType}`);
          }
          subgraphData = response.data;
          // 存入缓存
          this.subgraphCache.set(cacheKey, subgraphData);
        }
        
        this.isSubgraphMode = true;
        this.renderGraph(subgraphData);
      } catch (error) {
        console.error('获取节点子图失败:', error);
      }
    },

    // 添加一个新的方法来处理视图重置
    handleResetView() {
      this.isSubgraphMode = false;
      this.renderGraph(this.fullGraphData);
    },

    // 修改抽屉关闭处理方法，只处理节点选择状态
    handleDrawerClose() {
      this.selectedNode = null;
    },

    renderGraph(data) {
      console.log('初始化图谱，数据:', data);
      
      // 数据验证
      if (!data || !data.nodes || !data.links) {
        console.error('图谱数据不完整');
        return;
      }

      // 获取容器并验证
      const container = this.$refs.graphContainer;
      if (!container) {
        console.error('找不到图谱容器元素');
        return;
      }
      const width = container.clientWidth;
      const height = container.clientHeight;

      // 清除已存在的SVG并创建新的
      d3.select(container).selectAll('svg').remove();
      this.svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

      // 创建力导向图模拟
      // strength(-300)设置排斥力，负值表示节点间相互排斥
      this.simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id))  // 连接力
        .force('charge', d3.forceManyBody().strength(-3000))  // 节点间作用力
        .force('center', d3.forceCenter(width / 2, height / 2));  // 中心力

      // 添加箭头标记定义
      this.svg.append("defs").append("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 25) // 调整箭头位置
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", "#999");

      // 绘制带箭头的连接线
      const links = this.svg.append('g')
        .selectAll('line')
        .data(data.links)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-width', 1)
        .attr('marker-end', 'url(#arrow)'); // 添加箭头

      // 绘制节点
      const nodes = this.svg.append('g')  // 创建一个新的g元素来包含所有节点
        .selectAll('circle')  // 选择所有circle元素(此时还没有)
        .data(data.nodes)  // 绑定nodes数据到选择集
        .enter()  // 对于新数据创建circle元素
        .append('circle')  // 为每个数据项添加circle元素
        .attr('r', 20)  // 设置节点半径为20像素
        .attr('fill', d => d.color)  // 根据节点数据中的color属性设置填充颜色
        .on('click', (event, d) => {
          this.selectedNode = d;
          this.drawerVisible = true;
          
          if (!this.isSubgraphMode) {
            this.showNodeSubgraph(d.id, d.type);
          }
        })
        .call(d3.drag()  // 添加拖拽功能
          .on('start', this.dragstarted)  // 拖拽开始时触发dragstarted方法
          .on('drag', this.dragged)  // 拖拽过程中触发dragged方法
          .on('end', this.dragended));  // 拖拽结束时触发dragended方法

      // 添加节点文本标签
      const labels = this.svg.append('g')
        .selectAll('text')
        .data(data.nodes)
        .enter()
        .append('text')
        .text(d => d.name)
        .attr('font-size', 14)
        .attr('dx', 8)  // 文本X轴偏移
        .attr('dy', 4); // 文本Y轴偏移

      // 力导向图更新时的位置计算
      this.simulation.on('tick', () => {
        // 更新连接线位置
        links
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y);

        // 更新节点位置
        nodes
          .attr('cx', d => d.x)
          .attr('cy', d => d.y);

        // 更新标签位置
        labels
          .attr('x', d => d.x)
          .attr('y', d => d.y);
      });
      
      // 添加缩放功能
      // scaleExtent设置缩放范围：[最小缩放比例, 最大缩放比例]
      const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
          this.svg.selectAll('g').attr('transform', event.transform);
        });
      
      this.svg.call(zoom);
    },
  }
};
</script>

<style scoped>
.knowledge-container {
  height: 100%;
  padding: 20px;
  position: relative;
}

.knowledge-wrapper {
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.control-panel {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.upload-button {
  display: inline-block;
}

.search-box {
  width: 300px;
}

.graph-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.node-details {
  padding: 20px;
}

.detail-section {
  margin-top: 20px;
}

.detail-item {
  margin-bottom: 16px;
}

.detail-item label {
  display: block;
  font-weight: bold;
  color: #666;
  margin-bottom: 8px;
}

.detail-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

/* 自定义滚动条样式 */
.detail-content::-webkit-scrollbar {
  width: 6px;
}

.detail-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.detail-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.detail-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 添加拖拽区域样式 */
.graph-container.drag-mode {
  border: 2px dashed #409EFF;
}
</style> 