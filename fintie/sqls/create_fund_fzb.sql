CREATE TABLE IF NOT EXISTS fund_fzb (
    code                                                        TEXT,
    pub_date                                                    DATE,
    report_period                                               TIMESTAMP,

    -- 流动资产
    ca_cash                                                     BIGINT,
    ca_financial_current_profits_losses                         BIGINT,
    ca_bill_receivable                                          BIGINT,
    ca_accts_receivable                                         BIGINT,
    ca_advanced_accts_payable                                   BIGINT,
    ca_other_accts_receivable                                   BIGINT,
    receivables_from_associated_companies                       BIGINT,
    ca_interest_receivable                                      BIGINT,
    ca_devidend_receivable                                      BIGINT,
    ca_inventory                                                BIGINT,
    ca_expendable_biological_assets                             BIGINT,
    ca_non_ca_due_one_year                                      BIGINT,
    ca_others                                                   BIGINT,
    current_assets                                              BIGINT,

    -- 非流动资产
    nca_financial_asset_available_for_sale                      BIGINT,
    nca_financial_asset_hold_to_maturity                        BIGINT,
    nca_long_term_receivable                                    BIGINT,
    nca_long_term_equity_investment                             BIGINT,
    nca_real_estate_investment                                  BIGINT,
    nca_fixed_assets                                            BIGINT,
    nca_construction_in_progress                                BIGINT,
    nca_engineer_material                                       BIGINT,
    nca_fixed_asset_to_be_disposed                              BIGINT,
    nca_capitalized_biological_assets                           BIGINT,
    nca_oil_and_gas_assets                                      BIGINT,
    nca_intangible_assets                                       BIGINT,
    nca_impairment_intangible_assets                            BIGINT,
    nca_goodwill                                                BIGINT,
    nca_long_term_deferred_expenses                             BIGINT,
    nca_deferred_income_tax_assets                              BIGINT,
    nca_other_nca                                               BIGINT,
    non_current_assets                                          BIGINT,
    total_asset                                                 BIGINT,

    -- 流动负债
    cl_short_term_loans                                         BIGINT,
    cl_financial_liability                                      BIGINT,
    cl_notes_payable                                            BIGINT,
    cl_accts_payable                                            BIGINT,
    cl_advanced_accts_received                                  BIGINT,
    cl_payroll_payable                                          BIGINT,
    cl_tax_payable                                              BIGINT,
    cl_interest_payable                                         BIGINT,
    cl_dividend_payable                                         BIGINT,
    cl_other_payable                                            BIGINT,
    cl_payable_to_associated_companies                          BIGINT,
    cl_ncl_in_one_year                                          BIGINT,
    cl_others                                                   BIGINT,
    current_liability                                           BIGINT,

    -- 非流动负债
    ncl_long_term_loans                                         BIGINT,
    ncl_bond_payable                                            BIGINT,
    ncl_long_term_payable                                       BIGINT,
    ncl_grants_received                                         BIGINT,
    ncl_estimated_liability                                     BIGINT,
    ncl_deferred_income_tax_liability                           BIGINT,
    ncl_others                                                  BIGINT,
    non_current_liability                                       BIGINT,
    total_liability                                             BIGINT,

    equity_paid_in_capital                                      BIGINT,

    -- 所有者权益
    equity_capital_reserve                                      BIGINT,
    equity_surplus_reserve                                      BIGINT,
    equity_special_reserve                                      BIGINT,
    equity_treasury_stock                                       BIGINT,
    equity_general_risk_preparation                             BIGINT,
    equity_undistributed_profit                                 BIGINT,
    equity_parent_company                                       BIGINT,
    equity_minority_interest                                    BIGINT,
    equity_foreign_currency_spread                              BIGINT,
    equity_abnormal_operate_income_adjustment                   BIGINT,
    total_equity                                                BIGINT,
    total_equity_and_liability                                  BIGINT,
    equity_other_composite_income                               BIGINT,

    ncl_deferred_revenue                                        BIGINT,
    ca_deposit_reservation_for_balance                          BIGINT,
    ca_lendings_to_banks                                        BIGINT,
    ca_loans_and_advances                                       BIGINT,
    ca_financial_derivative                                     BIGINT,
    ca_insurance_receivable                                     BIGINT,
    ca_reinsurance_receivable                                   BIGINT,
    ca_reinsurance_contract_reserve_receivable                  BIGINT,
    ca_financial_assets_bought_back_of_sale                     BIGINT,
    ca_held_for_sale                                            BIGINT,
    nca_loans_and_advances                                      BIGINT,
    cl_borrowing_from_central_bank                              BIGINT,
    cl_deposit_in_interbank                                     BIGINT,
    cl_loans_from_other_banks                                   BIGINT,
    cl_derivative_financial_liability                           BIGINT,
    cl_financial_assets_sold_for_repurchase                     BIGINT,
    cl_commission_payable                                       BIGINT,
    cl_reinsurance_payable                                      BIGINT,
    cl_insurance_contract_reserve                               BIGINT,
    cl_acting_trading_security                                  BIGINT,
    cl_acting_underwriting_security                             BIGINT,
    cl_liabilities_held_for_sale                                BIGINT,
    cl_current_liability_estimated                              BIGINT,
    cl_deferred_revenue                                         BIGINT,
    ncl_preferred_share                                         BIGINT,
    ncl_perpetual_bonds                                         BIGINT,
    ncl_long_term_payable_of_staff                              BIGINT,
    equity_other_instruments                                    BIGINT,
    equity_preferred_share                                      BIGINT,
    equity_prepetual_bonds                                      BIGINT,
    UNIQUE (code, report_period)
);

/*
资产负债表（balance_sheet）

机构ID
机构名称
公告日期
截止日期
报告年度
合并类型
报表来源
-- 流动资产
ca_cash  货币资金（元）
    是指在企业生产经营过程中处于货币形态的那部分资金，
    按其形态和用途不同可分为包括库存现金、银行存款和其他货币资金。
ca_financial_current_profits_losses    以公允价值计量且其变动计入当期损益的金融资产
ca_bill_receivable  应收票据
    指企业持有的还没有到期、尚未兑现的票据。
    应收票据是企业未来收取货款的权利，
    这种权利和将来应收取的货款金额以书面文件形式约定下来，
    因此它受到法律的保护，具有法律上的约束力。是一种债权凭证。
ca_accts_receivable     应收账款
    指企业在正常的经营过程中因销售商品、产品、提供劳务等业务，应向购买单位收取的款项，
    包括应由购买单位或接受劳务单位负担的税金、代购买方垫付的各种运杂费等。
ca_advanced_accts_payable   预付款项
ca_other_accts_receivable   其他应收款
    是企业除应收票据、应收账款和预付账款以外的各种应收暂付款项。
receivables_from_associated_companies      应收关联公司款
ca_interest_receivable  应收利息
    短期债券投资实际支付的价款中包含的已到付息期但尚未领取的债券利息。
ca_devidend_receivable  应收股利
    指企业因股权投资而应收取的现金股利以及应收其他单位的利润，
    包括企业购入股票实际支付的款项中所包括的已宣告发放但尚未领取的现金股利和
    企业因对外投资应分得的现金股利或利润等，但不包括应收的股票股利。
ca_inventory    存货
    指企业在日常活动中持有的以备出售的产成品或商品、处在生产过程中的在产品、
    在生产过程或提供劳务过程中耗用的材料和物料等。
ca_expendable_biological_assets   其中：消耗性生物资产
ca_non_ca_due_one_year    一年内到期的非流动资产
    一年内到期的非流动资产反映企业将于一年内到期的非流动资产项目金额。
    包括一年内到期的持有至到期投资、长期待摊费用和一年内可收回的长期应收款
ca_others    其他流动资产
    指除货币资金、短期投资、应收票据、应收账款、其他应收款、存货等流动资产以外的流动资产。
current_assets   流动资产合计
    指企业可以在一年内或者超过一年的一个营业周期内变现或者耗用的资产，
    主要包括：现金及各种存款、短期投资、应收票据、应收帐款、预付账款、
              其他应收款、存货、待摊费用、待处理流动资产净损失、
              一年内到期的长期债权投资、其他流动资产等项。

-- 非流动资产
nca_financial_asset_available_for_sale  可供出售金融资产
    指初始确认时即被指定为可供出售的非衍生金融资产，
    以及贷款和应收款项、持有至到期投资、交易性金融资产之外的非衍生金融资产。
nca_financial_asset_hold_to_maturity    持有至到期投资
    指企业有明确意图并有能力持有至到期，到期日固定、回收金额固定或可确定的非衍生金融资产。
nca_long_term_receivable   长期应收款
    长期应收款是根据长期应收款的账户余额减去未确认融资收益还有一年内到期的长期应收款
nca_long_term_equity_investment     长期股权投资
    指企业持有的对其子公司、
    合营企业及联营企业的权益性投资以及企业持有的对被投资单位不具有控制、
    共同控制或重大影响，且在活跃市场中没有报价、公允价值不能可靠计量的权益性投资。
nca_real_estate_investment  投资性房地产
    指为赚取租金或资本增值，或两者兼有而持有的房地产。
nca_fixed_assets   固定资产
nca_construction_in_progress    在建工程
    指企业固定资产的新建、改建、扩建，或技术改造、设备更新和大修理工程等尚未完工的工程支出。
nca_engineer_material   工程物资
    指用于固定资产建造的建筑材料，如钢材、水泥、玻璃等。在资产负债表中并入在建工程项目。
nca_fixed_asset_to_be_disposed  固定资产清理
    指企业因出售、报废和毁损等原因转入清理的固定资产价值及其在清理过程中所发生的清理费用和清理收入等。
nca_capitalized_biological_assets   生产性生物资产
    指为产出农产品、提供劳务或出租等目的而持有的生物资产，包括经济林、薪炭林、产畜和役畜等。
nca_oil_and_gas_assets  油气资产
    指油气开采企业所拥有或控制的井及相关设施和矿区权益。油气资产属于递耗资产。
nca_intangible_assets   无形资产
    指企业拥有或者控制的没有实物形态的可辨认非货币性资产。
nca_impairment_intangible_assets    开发支出
    反映企业开发无形资产过程中能够资本化形成无形资产成本的支出部分。
nca_goodwill    商誉
    指能在未来期间为企业经营带来超额利润的潜在经济价值，
    或一家企业预期的获利能力超过可辨认资产正常获利能力（如社会平均投资回报率）的资本化价值。
nca_long_term_deferred_expenses     长期待摊费用
    指企业已经支出，但摊销期限在1年以上(不含1年)的各项费用，
    包括开办费、租入固定资产的改良支出及摊销期在1年以上的固定资产大修理支出、股票发行费用等。
nca_deferred_income_tax_assets  递延所得税资产
    指对于可抵扣暂时性差异，
    以未来期间很可能取得用来抵扣可抵扣暂时性差异的应纳税所得额为限确认的一项资产。
nca_other_nca    其他非流动资产
    指除资产负债表上所列非流动资产项目以外的其他周转期超过1年的长期资产。
non_current_assets  非流动资产合计

total_asset     资产总计

-- 流动负债
cl_short_term_loans    短期借款
    企业用来维持正常的生产经营所需的资金或为抵偿某项债务而向银行或其他金融机构等外单位借入的、
    还款期限在一年以下或者一年的一个经营周期内的各种借款。
cl_financial_liability           以公允价值计量且其变动计入当期损益的金融负债
cl_notes_payable   应付票据
    应付票据是指企业购买材料、商品和接受劳务供应等而开出、承兑的商业汇票，
    包括商业承兑汇票和银行承兑汇票。
    在我国应收票据、应付票据仅指"商业汇票"，包括"银行承兑汇票"和"商业承兑汇票"两种，
    属于远期票据，付款期一般在1个月以上，6个月以内。
cl_accts_payable   应付账款
    应付帐款是指企业因购买材料、物资和接受劳务供应等而付给供货单位的帐款。
cl_advanced_accts_received  预收款项
cl_payroll_payable     应付职工薪酬
    应付职工薪酬是指企业为获得职工提供的服务而给予各种形式的报酬以及其他相关支出。
    职工薪酬包括：职工工资、奖金、津贴和补贴；
    职工福利费；医疗保险费、养老保险费、失业保险费、工伤保险费和生育保险费等社会保险费；
    住房公积金；工会经费和职工教育经费；非货币性福利；
    因解除与职工的劳动关系给予的补偿；其他与获得职工提供的服务相关的支出。
cl_tax_payable     应交税费
    应交税费是指企业根据在一定时期内取得的营业收入、实现的利润等，
    按照现行税法规定，采用一定的计税方法计提的应交纳的各种税费。
cl_interest_payable    应付利息
    应付利息，是指金融企业根据存款或债券金额及其存续期限和规定的利率，
    按期计提应支付给单位和个人的利息。
    应付利息应按已计但尚未支付的金额入账。
    应付利息包括分期付息到期还本的长期借款、企业债券等应支付的利息。
    应付利息与应计利息的区别：应付利息属于借款 应计利息属于企业存款。
cl_dividend_payable    应付股利
    应付股利是指企业根据年度利润分配方案，确定分配的股利。
    是企业经董事会或股东大会，或类似机构决议确定分配的现金股利或利润。
    企业分配的股票股利，不通过"应付股利"科目核算。
cl_other_payable   其他应付款
    其他应付款是财务会计中的一个往来科目，通常情况下，
    该科目只核算企业应付其他单位或个人的零星款项，
    如应付经营租入固定资产和包装物的租金、存入保证金、应付统筹退休金等。
    企业经常发生的应付供应单位的货款是在"应付帐款"和"应付票据"科目中核算
cl_payable_to_associated_companies     应付关联公司款
cl_ncl_in_one_year   一年内到期的非流动负债
    是反映企业各种非流动负债在一年之内到期的金额，
    包括一年内到期的长期借款、长期应付款和应付债券。本项目应根据上述账户分析计算后填列。
    计入(收录)流动负债中。
cl_others   其他流动负债
    其他流动负债是指不能归属于短期借款，应付短期债券券，应付票据，
    应付帐款，应付所得税，其他应付款，预收账款这七款项目的流动负债。
    但以上各款流动负债，其金额未超过流动负债合计金额百分之五者，得并入其他流动负债内。
current_liability     流动负债合计
    流动负债合计是指企业在一年内或超过一年的一个营业周期内需要偿还的债务，
    包括短期借款、应付帐款、其他应付款、应付工资、应付福利费、未交税金和未付利润、其他应付款、预提费用等。

-- 非流动负债
ncl_long_term_loans     长期借款
    长期借款是指企业从银行或其他金融机构借入的期限在一年以上(不含一年)的借款。
    我国股份制企业的长期借款主要是向金融机构借人的各项长期性借款，
    如从各专业银行、商业银行取得的贷款；除此之外，还包括向财务公司、投资公司等金融企业借人的款项。
ncl_bond_payable    应付债券
    公司为筹集长期资金而实际发行的债券及应付的利息。。
ncl_long_term_payable   长期应付款
    长期应付款是指企业除了长期借款和应付债券以外的长期负债，包括应付引进设备款、应付融资租入固定资产的租赁费等。
ncl_grants_received     专项应付款
    专项应付款是企业接受国家作为企业所有者拨入的具有专门用途的款项所形成的不需要以资产或增加其他负债偿还的负债。
ncl_estimated_liability   预计负债
    预计负债是因或有事项可能产生的负债。
ncl_deferred_income_tax_liability     递延所得税负债
    递延所得税负债是指根据应纳税暂时性差异计算的未来期间应付所得税的金额；
ncl_others  其他非流动负债
    其他非流动负债项目是反映企业除长期借款、应付债券等项目以外的其他非流动负债。
    其他非流动负债项目应根据有关科目的期末余额填列。
    其他非流动负债项目应根据有关科目期末余额减去将于一年内（含一年）到期偿还数后的余额填列。
    非流动负债各项目中将于一年内（含一年）到期的非流动负债，应在"一年内到期的非流动负债"项目内单独反映。
non_current_liability     非流动负债合计
    非流动负债是指偿还期在一年或者超过一年的一个营业周期以上的债务。非流动负债的主要项目有长期借款和应付债券。

total_liability   负债合计
    负债合计是指企业所承担的能以货币计量，将以资产或劳务偿还的债务，
    偿还形式包括货币、资产或提供劳务。根据会计"资产负债表"中"负债合计"项的年末数填列。

equity_paid_in_capital     实收资本（或股本）
    实收资本是指企业的投资者按照企业章程或合同、协议的约定，实际投入企业的资本。

-- 所有者权益
equity_capital_reserve     资本公积
    资本公积是企业收到的投资者的超出其在企业注册资本所占份额，
    以及直接计入所有者权益的利得和损失等。
    资本公积包括资本溢价（股本溢价）和直接计入所有者权益的利得和损失等。
equity_surplus_reserve     盈余公积
    盈余公积是指企业从税后利润中提取形成的、存留于企业内部、具有特定用途的收益积累。
    盈余公积是根据其用途不同分为公益金和一般盈余公积两类。
equity_special_reserve     专项储备
equity_treasury_stock      减：库存股
equity_general_risk_preparation    一般风险准备
equity_undistributed_profit    未分配利润
    未分配利润是企业未作分配的利润。
    它在以后年度可继续进行分配，在未进行分配之前，属于所有者权益的组成部分。
    从数量上来看，未分配利润是期初未分配利润加上本期实现的净利润，
    减去提取的各种盈余公积和分出的利润后的余额。
equity_parent_company       归属于母公司所有者权益
    母公司股东权益反映的是母公司所持股份部分的所有者权益数，
    所有者权益合计是反映的是所有的股东包括母公司与少数股东一起100%的股东
    所持股份的总体所有者权益合计数。即所有者权益合计＝母公司股东权益合计母＋少数股东权益合计。
equity_minority_interest   少数股东权益
    少数股东损益是一个流量概念，
    是指公司合并报表的子公司其它非控股股东享有的损益，需要在利润表中予以扣除。
    利润表的"净利润"项下可以分"归属于母公司所有者的净利润"和"少数股东损益"。
    其对应的存量概念是"少数股东权益"。
equity_foreign_currency_spread       外币报表折算价差
equity_abnormal_operate_income_adjustment    非正常经营项目收益调整
total_equity    所有者权益（或股东权益）合计
    所有者权益合计是指企业投资人对企业净资产的所有权。
    企业净资产等于企业全部资产减去全部负债后的余额，
    其中包括企业投资人对企业的最初投入以及资本公积金、盈余公积金和未分配利润。
    对股份制企业，所有者权益即为股东权益。
total_equity_and_liability    负债和所有者（或股东权益）合计
equity_other_composite_income      其他综合收益

ncl_deferred_revenue    递延收益-非流动负债
    递延收益是指尚待确认的收入或收益，也可以说是暂时未确认的收益，它是权责发生制在收益确认上的运用。
ca_deposit_reservation_for_balance     结算备付金
ca_lendings_to_banks   拆出资金
ca_loans_and_advances     发放贷款及垫款-流动资产
ca_financial_derivative    衍生金融资产
ca_insurance_receivable   应收保费
ca_reinsurance_receivable     应收分保账款
ca_reinsurance_contract_reserve_receivable    应收分保合同准备金
    是用于核算企业（再保险分出人）从事再保险业务确认的应收分保未到期责任准备金，
    以及应向再保险接受人摊回的保险责任准备金。
ca_financial_assets_bought_back_of_sale    买入返售金融资产
ca_held_for_sale   划分为持有待售的资产
nca_loans_and_advances      发放贷款及垫款-非流动资产
cl_borrowing_from_central_bank 向中央银行借款
cl_deposit_in_interbank    吸收存款及同业存放
cl_loans_from_other_banks  拆入资金
cl_derivative_financial_liability   衍生金融负债
cl_financial_assets_sold_for_repurchase    卖出回购金融资产款
cl_commission_payable  应付手续费及佣金
cl_reinsurance_payable    应付分保账款
cl_insurance_contract_reserve     保险合同准备金
cl_acting_trading_security   代理买卖证券款
cl_acting_underwriting_security  代理承销证券款
cl_liabilities_held_for_sale  划分为持有待售的负债
cl_current_liability_estimated   预计负债-流动负债
cl_deferred_revenue     递延收益-流动负债
ncl_preferred_share  其中：优先股-非流动负债
ncl_perpetual_bonds     永续债-非流动负债
ncl_long_term_payable_of_staff     长期应付职工薪酬
equity_other_instruments   其他权益工具
equity_preferred_share  其中：优先股-所有者权益
equity_prepetual_bonds  永续债-所有者权益
*/
