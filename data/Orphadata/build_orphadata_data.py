import os
import requests
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import xml.etree.ElementTree as ET

class OrphadataDownloader:
    def __init__(self, base_folder='orphadata', max_workers=5):
        self.base_folder = base_folder
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 定义所有下载任务（相对路径）
        self.downloads = [
            # Rare diseases and alignment
            {
                'url': 'https://www.orphadata.com/data/xml/en_product1.xml',
                'folder': 'Rare diseases and alignment',
                'filename': 'en_product1.xml'
            },
            {
                'url': 'https://www.orphadata.com/data/xml/zh_product1.xml',
                'folder': 'Rare diseases and alignment',
                'filename': 'zh_product1.xml'
            },
            {
                'url': 'https://www.orphadata.com/data/json/en_product1.json.tar.gz',
                'folder': 'Rare diseases and alignment',
                'filename': 'en_product1.json.tar.gz'
            },
            {
                'url': 'https://www.orphadata.com/data/json/zh_product1.json.tar.gz',
                'folder': 'Rare diseases and alignment',
                'filename': 'zh_product1.json.tar.gz'
            },
            # Linearisation of Rare Diseases
            {
                'url': 'https://www.orphadata.com/data/xml/en_product7.xml',
                'folder': 'Linearisation of Rare Diseases',
                'filename': 'en_product7.xml'
            },
            # Genes Associated with Rare Diseases
            {
                'url': 'https://www.orphadata.com/data/xml/en_product6.xml',
                'folder': 'Genes Associated with Rare Diseases',
                'filename': 'en_product6.xml'
            },
            # Phenotypes Associated with Rare Disorders
            {
                'url': 'https://www.orphadata.com/data/xml/en_product4.xml',
                'folder': 'Phenotypes Associated with Rare Disorders',
                'filename': 'en_product4.xml'
            },
            # Rare Diseases and Functional Consequences
            {
                'url': 'https://www.orphadata.com/data/xml/en_funct_consequences.xml',
                'folder': 'Rare Diseases and Functional Consequences',
                'filename': 'en_funct_consequences.xml'
            },
            # Epidemiology of Rare Diseases
            {
                'url': 'https://www.orphadata.com/data/xml/en_product9_prev.xml',
                'folder': 'Epidemiology of Rare Diseases',
                'filename': 'en_product9_prev.xml'
            },
            # Natural History of Rare Diseases
            {
                'url': 'https://www.orphadata.com/data/xml/en_product9_ages.xml',
                'folder': 'Natural History of Rare Diseases',
                'filename': 'en_product9_ages.xml'
            },
        ]
        
        # Classifications of Rare Diseases (子分类)
        classifications = [
            ('en_product3_146.xml', 'Rare cardiac diseases'),
            ('en_product3_147.xml', 'Rare developmental anomalies during embryogenesis'),
            ('en_product3_148.xml', 'Rare cardiac malformations'),
            ('en_product3_150.xml', 'Rare inborn errors of metabolism'),
            ('en_product3_152.xml', 'Rare gastroenterological diseases'),
            ('en_product3_156.xml', 'Rare genetic diseases'),
            ('en_product3_181.xml', 'Rare neurological diseases'),
            ('en_product3_182.xml', 'Rare abdominal surgical diseases'),
            ('en_product3_183.xml', 'Rare hepatic diseases'),
            ('en_product3_184.xml', 'Rare respiratory diseases'),
            ('en_product3_185.xml', 'Rare urogenital diseases'),
            ('en_product3_186.xml', 'Rare surgical thoracic diseases'),
            ('en_product3_187.xml', 'Rare skin diseases'),
            ('en_product3_188.xml', 'Rare renal diseases'),
            ('en_product3_189.xml', 'Rare ophthalmic diseases'),
            ('en_product3_193.xml', 'Rare endocrine diseases'),
            ('en_product3_194.xml', 'Rare haematological diseases'),
            ('en_product3_195.xml', 'Rare immunological diseases'),
            ('en_product3_196.xml', 'Rare systemic and rhumatological diseases'),
            ('en_product3_197.xml', 'Rare odontological diseases'),
            ('en_product3_198.xml', 'Rare circulatory system diseases'),
            ('en_product3_199.xml', 'Rare bone diseases'),
            ('en_product3_200.xml', 'Rare otorhinolaryngological diseases'),
            ('en_product3_201.xml', 'Rare infertility'),
            ('en_product3_202.xml', 'Rare neoplastic diseases'),
            ('en_product3_203.xml', 'Rare infectious diseases'),
            ('en_product3_204.xml', 'Rare diseases due to toxic effects'),
            ('en_product3_205.xml', 'Rare gynaecological and obstetric diseases'),
            ('en_product3_209.xml', 'Rare surgical maxillo-facial diseases'),
            ('en_product3_212.xml', 'Rare allergic disease'),
            ('en_product3_216.xml', 'Rare teratologic disorders'),
            ('en_product3_231.xml', 'Rare systemic and rheumatological diseases of childhood'),
            ('en_product3_233.xml', 'Rare transplant-related diseases'),
            ('en_product3_235.xml', 'Rare disorder without a determined diagnosis after full investigation'),
        ]
        
        for filename, subfolder in classifications:
            self.downloads.append({
                'url': f'https://www.orphadata.com/data/xml/{filename}',
                'folder': f'Classifications of Rare Diseases/{subfolder}',
                'filename': filename
            })
    
    def get_full_path(self, relative_folder):
        """获取完整路径（基础文件夹 + 相对路径）"""
        return os.path.join(self.base_folder, relative_folder)
    
    def create_folders(self):
        """创建所有必要的文件夹"""
        print("\n=== 创建文件夹结构 ===")
        print(f"基础文件夹: {self.base_folder}\n")
        
        # 创建基础文件夹
        Path(self.base_folder).mkdir(parents=True, exist_ok=True)
        
        folders = set([self.get_full_path(item['folder']) for item in self.downloads])
        for folder in sorted(folders):
            Path(folder).mkdir(parents=True, exist_ok=True)
            # 显示相对于基础文件夹的路径
            relative_path = os.path.relpath(folder, self.base_folder)
            print(f"✓ {self.base_folder}/{relative_path}")
        
        print(f"\n总共创建/检查了 {len(folders)} 个子文件夹\n")
    
    def check_file_exists(self, filepath):
        """检查文件是否存在且大小大于0"""
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            if size > 0:
                return True, size
        return False, 0
    
    def validate_file(self, filepath, filename):
        """验证文件是否有效"""
        try:
            size = os.path.getsize(filepath)
            
            # 文件太小肯定有问题
            if size < 100:
                return False, "文件过小"
            
            # 验证 XML 文件
            if filename.endswith('.xml'):
                try:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    # XML 文件至少要有根元素
                    if root is None:
                        return False, "XML 文件无效"
                except ET.ParseError as e:
                    return False, f"XML 解析错误: {str(e)}"
            
            # 验证 tar.gz 文件（检查文件头）
            elif filename.endswith('.tar.gz'):
                with open(filepath, 'rb') as f:
                    # tar.gz 文件应该以 0x1f 0x8b 开头（gzip magic number）
                    header = f.read(2)
                    if header != b'\x1f\x8b':
                        return False, "不是有效的 gzip 文件"
            
            return True, "有效"
            
        except Exception as e:
            return False, str(e)
    
    def download_file(self, task):
        """下载单个文件"""
        url = task['url']
        folder = task['folder']
        filename = task['filename']
        full_folder = self.get_full_path(folder)
        filepath = os.path.join(full_folder, filename)
        
        # 检查文件是否已存在且有效
        exists, existing_size = self.check_file_exists(filepath)
        if exists:
            is_valid, msg = self.validate_file(filepath, filename)
            if is_valid:
                return {
                    'status': 'skipped',
                    'url': url,
                    'filepath': filepath,
                    'size': existing_size,
                    'filename': filename,
                    'folder': folder
                }
            else:
                # 文件存在但无效，删除后重新下载
                print(f"⚠ 文件已存在但无效，重新下载: {filename} ({msg})")
                try:
                    os.remove(filepath)
                except:
                    pass
        
        try:
            # 发送请求
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            
            # 下载文件
            downloaded_size = 0
            with open(filepath, 'wb') as f, tqdm(
                desc=filename[:50],
                total=total_size if total_size > 0 else None,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                leave=False
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        pbar.update(len(chunk))
            
            # 获取实际文件大小
            final_size = os.path.getsize(filepath)
            
            # 验证文件有效性（比大小检查更可靠）
            is_valid, msg = self.validate_file(filepath, filename)
            if not is_valid:
                os.remove(filepath)
                return {
                    'status': 'error',
                    'url': url,
                    'filepath': filepath,
                    'filename': filename,
                    'folder': folder,
                    'error': f'文件验证失败: {msg}'
                }
            
            # 如果声明了大小，但实际大小差异很大（小于预期的50%），可能有问题
            if total_size > 0 and final_size < total_size * 0.5:
                return {
                    'status': 'error',
                    'url': url,
                    'filepath': filepath,
                    'filename': filename,
                    'folder': folder,
                    'error': f'文件可能不完整: 预期约 {total_size} 字节, 实际 {final_size} 字节',
                    'size': final_size
                }
            
            return {
                'status': 'success',
                'url': url,
                'filepath': filepath,
                'size': final_size,
                'filename': filename,
                'folder': folder,
                'declared_size': total_size
            }
            
        except Exception as e:
            # 如果下载失败，删除可能不完整的文件
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            
            return {
                'status': 'error',
                'url': url,
                'filepath': filepath,
                'error': str(e),
                'filename': filename,
                'folder': folder
            }
    
    def download_all(self):
        """多线程下载所有文件"""
        print(f"=== 开始下载 ===")
        print(f"总文件数: {len(self.downloads)}")
        print(f"线程数: {self.max_workers}\n")
        
        results = {
            'success': [],
            'skipped': [],
            'error': []
        }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self.download_file, task): task 
                for task in self.downloads
            }
            
            # 使用tqdm显示总体进度
            with tqdm(total=len(self.downloads), desc="总体进度", unit="文件") as pbar:
                for future in as_completed(future_to_task):
                    try:
                        result = future.result()
                        results[result['status']].append(result)
                        
                        # 打印每个文件的状态
                        if result['status'] == 'success':
                            size_mb = result['size'] / (1024 * 1024)
                            declared = result.get('declared_size', 0)
                            if declared > 0 and abs(declared - result['size']) > 1000:
                                print(f"✓ 下载成功: {result['filename']} ({size_mb:.2f} MB) "
                                      f"[声明: {declared/1024:.1f}KB, 实际: {result['size']/1024:.1f}KB]")
                            else:
                                print(f"✓ 下载成功: {result['filename']} ({size_mb:.2f} MB)")
                        elif result['status'] == 'skipped':
                            size_mb = result['size'] / (1024 * 1024)
                            print(f"⊙ 已存在: {result['filename']} ({size_mb:.2f} MB)")
                        else:
                            print(f"✗ 下载失败: {result['filename']} - {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        task = future_to_task[future]
                        print(f"✗ 处理异常: {task['filename']} - {str(e)}")
                        results['error'].append({
                            'status': 'error',
                            'url': task['url'],
                            'filename': task['filename'],
                            'folder': task['folder'],
                            'error': str(e)
                        })
                    
                    pbar.update(1)
        
        elapsed_time = time.time() - start_time
        
        # 打印汇总报告
        self.print_summary(results, elapsed_time)
        
        return results
    
    def print_summary(self, results, elapsed_time):
        """打印下载汇总报告"""
        print("\n" + "="*70)
        print("=== 下载汇总报告 ===")
        print("="*70)
        
        print(f"\n总文件数: {len(self.downloads)}")
        print(f"✓ 成功下载: {len(results['success'])} 个文件")
        print(f"⊙ 已存在跳过: {len(results['skipped'])} 个文件")
        print(f"✗ 下载失败: {len(results['error'])} 个文件")
        print(f"\n总耗时: {elapsed_time:.2f} 秒")
        
        # 计算总下载大小
        total_downloaded = sum(r.get('size', 0) for r in results['success'])
        total_existing = sum(r.get('size', 0) for r in results['skipped'])
        
        print(f"\n本次下载: {total_downloaded / (1024*1024):.2f} MB")
        print(f"已有文件: {total_existing / (1024*1024):.2f} MB")
        print(f"总计: {(total_downloaded + total_existing) / (1024*1024):.2f} MB")
        
        # 如果有失败的文件，列出详情
        if results['error']:
            print("\n" + "="*70)
            print("=== 失败文件列表 ===")
            print("="*70)
            for i, result in enumerate(results['error'], 1):
                print(f"\n{i}. 文件: {result.get('filename', 'Unknown')}")
                print(f"   URL: {result.get('url', 'Unknown')}")
                print(f"   错误: {result.get('error', 'Unknown error')}")
        
        # 按文件夹统计
        print("\n" + "="*70)
        print("=== 按文件夹统计 ===")
        print("="*70)
        
        folder_stats = {}
        for task in self.downloads:
            folder = task['folder']
            if folder not in folder_stats:
                folder_stats[folder] = {'total': 0, 'success': 0, 'skipped': 0, 'error': 0}
            folder_stats[folder]['total'] += 1
        
        for result_list in [results['success'], results['skipped'], results['error']]:
            for result in result_list:
                folder = result.get('folder', '')
                if folder in folder_stats:
                    folder_stats[folder][result['status']] += 1
        
        for folder, stats in sorted(folder_stats.items()):
            status = "✓" if stats['error'] == 0 else "✗"
            print(f"\n{status} {self.base_folder}/{folder}")
            print(f"   总计: {stats['total']} | 成功: {stats['success']} | "
                  f"跳过: {stats['skipped']} | 失败: {stats['error']}")
        
        print("\n" + "="*70)
        
        if results['error']:
            print("\n⚠ 有文件下载失败，请重新运行脚本继续下载")
        else:
            print("\n✓ 所有文件下载完成！")
        
        print("="*70 + "\n")
    
    def verify_downloads(self):
        """验证所有下载的文件"""
        print("\n=== 验证下载文件 ===")
        
        missing_files = []
        invalid_files = []
        valid_files = []
        
        for task in self.downloads:
            full_folder = self.get_full_path(task['folder'])
            filepath = os.path.join(full_folder, task['filename'])
            exists, size = self.check_file_exists(filepath)
            
            if not exists:
                missing_files.append(task['filename'])
            else:
                is_valid, msg = self.validate_file(filepath, task['filename'])
                if not is_valid:
                    invalid_files.append((task['filename'], msg))
                else:
                    valid_files.append((task['filename'], size))
        
        print(f"\n✓ 有效文件: {len(valid_files)}/{len(self.downloads)}")
        print(f"✗ 缺失文件: {len(missing_files)}")
        print(f"⚠ 无效文件: {len(invalid_files)}")
        
        if missing_files:
            print("\n缺失文件列表:")
            for filename in missing_files:
                print(f"  - {filename}")
        
        if invalid_files:
            print("\n无效文件列表:")
            for filename, msg in invalid_files:
                print(f"  - {filename}: {msg}")
        
        return len(missing_files) == 0 and len(invalid_files) == 0

def main():
    print("="*70)
    print("Orphadata 数据下载器")
    print("="*70)
    
    # 创建下载器实例（所有文件将下载到 orphadata 文件夹下）
    downloader = OrphadataDownloader(base_folder='orphadata', max_workers=5)
    
    # 创建文件夹
    downloader.create_folders()
    
    # 下载所有文件
    results = downloader.download_all()
    
    # 验证下载
    all_valid = downloader.verify_downloads()
    
    if not all_valid:
        print("\n💡 提示: 重新运行此脚本将只下载缺失或失败的文件")
    else:
        print("\n🎉 恭喜！所有文件下载并验证成功！")
    
    return results

if __name__ == "__main__":
    main()